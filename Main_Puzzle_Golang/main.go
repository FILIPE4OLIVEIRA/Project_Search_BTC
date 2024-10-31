package main

import (
	"bufio"
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"io/ioutil"
	"log"
	"math/big"
	"math/rand"
	"net/http"
	"os"
	"runtime"
	"strconv"
	"strings"
	"sync"
	"time"

	"github.com/btcsuite/btcd/chaincfg"
	"github.com/decred/dcrd/dcrec/secp256k1/v4"
	"github.com/dustin/go-humanize"
	"github.com/fatih/color"
	"golang.org/x/crypto/ripemd160"
)

// Wallets struct to hold the array of wallet addresses
type Wallets struct {
	Addresses []string `json:"wallets"`
}

// Range struct to hold the minimum, maximum, and status
type Range struct {
	Min    string `json:"min"`
	Max    string `json:"max"`
	Status int    `json:"status"`
}

// Ranges struct to hold an array of ranges
type Ranges struct {
	Ranges []Range `json:"ranges"`
}

func main() {

	white := color.New(color.FgWhite).SprintFunc()

	ranges, err := loadRanges("ranges.json")
	if err != nil {
		log.Fatalf("Failed to Load Ranges: %v", err)
	}

	// Ask the user for the range number
	rangeNumber := promptRangeNumber(len(ranges.Ranges))

	// Ask the user for the search method
	searchMode := promptSearchMode()

	// Initialize privKeyInt with the minimum value of the selected range
	minKeyHex := ranges.Ranges[rangeNumber-1].Min
	maxKeyHex := ranges.Ranges[rangeNumber-1].Max

	privKeyInt := new(big.Int)
	privKeyInt.SetString(minKeyHex[2:], 16)

	minKeyInt := new(big.Int)
	minKeyInt.SetString(minKeyHex[2:], 16)

	maxKeyInt := new(big.Int)
	maxKeyInt.SetString(maxKeyHex[2:], 16)

	// Load wallet addresses from JSON file
	wallets, err := loadWallets("wallets.json")
	if err != nil {
		log.Fatalf("Failed to Load Wallets: %v", err)
	}

	fileName := fmt.Sprintf("tested_keys_%d.txt", rangeNumber)
	TotalkeysChecked := getInitialKeysChecked(fileName)
	keysChecked := 0
	startTime := time.Now()

	// Number of CPU cores to use
	numCPU := runtime.NumCPU() / 2
	fmt.Printf("CPUs: %s\n", white(numCPU))
	fmt.Printf("Key Ranges Initial [0x%s] -- Final [0x%s]\n", minKeyInt.Text(16), maxKeyInt.Text(16))
	runtime.GOMAXPROCS(numCPU * 2)

	// Create a channel to send private keys to workers
	privKeyChan := make(chan *big.Int)
	// Create a channel to receive results from workers
	resultChan := make(chan *big.Int)
	// Create a wait group to wait for all workers to finish
	var wg sync.WaitGroup

	// Start worker goroutines
	for i := 0; i < numCPU*2; i++ {
		wg.Add(1)
		go worker(wallets, privKeyChan, resultChan, &wg)
	}

	// Ticker for periodic updates
	ticker := time.NewTicker(1 * time.Second)
	done := make(chan bool)

	var currentKey *big.Int

	// Goroutine to print speed updates
	go func() {
		for {
			select {
			case <-ticker.C:
				elapsedTime := time.Since(startTime).Seconds()
				keysPerSecond := float64(keysChecked) / elapsedTime
				TotalkeysChecked += int(keysPerSecond)
				fmt.Printf("[Current Key: 0x%s] || [Keys: %s] || [Keys/Seg: %s]\n",
					currentKey.Text(16),
					humanize.Comma(int64(TotalkeysChecked)),
					humanize.Comma(int64(keysPerSecond)))
			case <-done:
				ticker.Stop()
				return
			}
		}
	}()

	// Send private keys to the workers based on the search mode
	go func() {
		sequentialCount := 0
		for {
			if searchMode == 1 {
				currentKey = new(big.Int).Set(privKeyInt)
				privKeyChan <- currentKey
				privKeyInt.Add(privKeyInt, big.NewInt(1))
			} else if searchMode == 2 {
				privKeyInt := getRandomKeyInRange(minKeyInt, maxKeyInt)
				currentKey = new(big.Int).Set(privKeyInt)
				privKeyChan <- currentKey
				if keysChecked%100000 == 0 {
					saveTestedKeys(privKeyInt, rangeNumber)
				}
			} else {
				if sequentialCount == 0 || sequentialCount >= 25000000 {
					privKeyInt = getRandomKeyInRange(minKeyInt, maxKeyInt)
					sequentialCount = 0
				}
				currentKey = new(big.Int).Set(privKeyInt)
				privKeyChan <- currentKey
				privKeyInt.Add(privKeyInt, big.NewInt(1))
				sequentialCount++
				if keysChecked%25000000 == 0 {
					saveTestedKeys(privKeyInt, rangeNumber)
				}
			}
			keysChecked++
		}
	}()

	foundAddress := <-resultChan

	close(done)

	// Wait for all workers to finish
	go func() {
		wg.Wait()
		close(privKeyChan)
	}()

	walletAddress := createPublicAddress(foundAddress)
	privateKey := privateKeyToWIF(foundAddress)
	balance := checkBalance(walletAddress)

	printResults(foundAddress, walletAddress, privateKey, balance, keysChecked, startTime)
	saveTargetWallet(walletAddress, privateKey, balance)

}

func worker(wallets *Wallets, privKeyChan <-chan *big.Int, resultChan chan<- *big.Int, wg *sync.WaitGroup) {
	defer wg.Done()
	for privKeyInt := range privKeyChan {
		address := createPublicAddress(privKeyInt)
		if contains(wallets.Addresses, address) {
			resultChan <- privKeyInt
			return
		}
	}
}

func createPublicAddress(privKeyInt *big.Int) string {
	privKeyHex := fmt.Sprintf("%064x", privKeyInt)
	privKeyBytes, err := hex.DecodeString(privKeyHex)
	if err != nil {
		log.Fatal(err)
	}
	privKey := secp256k1.PrivKeyFromBytes(privKeyBytes)
	compressedPubKey := privKey.PubKey().SerializeCompressed()
	pubKeyHash := hash160(compressedPubKey)
	address := encodeAddress(pubKeyHash, &chaincfg.MainNetParams)

	return address

}

// hash160 computes the RIPEMD160(SHA256(b)) hash.
func hash160(b []byte) []byte {
	h := sha256.New()
	h.Write(b)
	sha256Hash := h.Sum(nil)

	r := ripemd160.New()
	r.Write(sha256Hash)
	return r.Sum(nil)
}

// encodeAddress encodes the public key hash into a Bitcoin address.
func encodeAddress(pubKeyHash []byte, params *chaincfg.Params) string {
	versionedPayload := append([]byte{params.PubKeyHashAddrID}, pubKeyHash...)
	checksum := doubleSha256(versionedPayload)[:4]
	fullPayload := append(versionedPayload, checksum...)
	return base58Encode(fullPayload)
}

// doubleSha256 computes SHA256(SHA256(b)).
func doubleSha256(b []byte) []byte {
	first := sha256.Sum256(b)
	second := sha256.Sum256(first[:])
	return second[:]
}

// base58Encode encodes a byte slice to a base58-encoded string.
var base58Alphabet = []byte("123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz")

func base58Encode(input []byte) string {
	var result []byte
	x := new(big.Int).SetBytes(input)

	base := big.NewInt(int64(len(base58Alphabet)))
	zero := big.NewInt(0)
	mod := &big.Int{}

	for x.Cmp(zero) != 0 {
		x.DivMod(x, base, mod)
		result = append(result, base58Alphabet[mod.Int64()])
	}

	// Reverse the result
	for i, j := 0, len(result)-1; i < j; i, j = i+1, j-1 {
		result[i], result[j] = result[j], result[i]
	}

	// Add leading zeros
	for _, b := range input {
		if b != 0 {
			break
		}
		result = append([]byte{base58Alphabet[0]}, result...)
	}

	return string(result)
}

// privateKeyToWIF converts a private key to Wallet Import Format (WIF)
func privateKeyToWIF(privKey *big.Int) string {
	prefix := []byte{0x80}
	privKeyBytes := privKey.FillBytes(make([]byte, 32))
	privKeyBytes = append(privKeyBytes, 0x01)
	extendedKey := append(prefix, privKeyBytes...)
	checksum := doubleSha256(extendedKey)[:4]
	fullKey := append(extendedKey, checksum...)
	wif := base58Encode(fullKey)
	return wif
}

// loadWallets loads wallet addresses from a JSON file
func loadWallets(filename string) (*Wallets, error) {
	file, err := os.Open(filename)
	if err != nil {
		return nil, err
	}
	defer file.Close()

	bytes, err := ioutil.ReadAll(file)
	if err != nil {
		return nil, err
	}

	var wallets Wallets
	if err := json.Unmarshal(bytes, &wallets); err != nil {
		return nil, err
	}

	return &wallets, nil
}

// contains checks if a string is in a slice of strings
func contains(slice []string, item string) bool {
	for _, a := range slice {
		if a == item {
			return true
		}
	}
	return false
}

// loadRanges loads ranges from a JSON file
func loadRanges(filename string) (*Ranges, error) {
	file, err := os.Open(filename)
	if err != nil {
		return nil, err
	}
	defer file.Close()

	bytes, err := ioutil.ReadAll(file)
	if err != nil {
		return nil, err
	}

	var ranges Ranges
	if err := json.Unmarshal(bytes, &ranges); err != nil {
		return nil, err
	}

	return &ranges, nil
}

// promptRangeNumber prompts the user to select a range number
func promptRangeNumber(totalRanges int) int {
	reader := bufio.NewReader(os.Stdin)
	charReadline := '\n'

	if runtime.GOOS == "windows" {
		charReadline = '\r'
	}

	for {
		fmt.Printf("Escolha a Wallet (1 a %d): ", totalRanges)
		input, _ := reader.ReadString(byte(charReadline))
		input = strings.TrimSpace(input)
		rangeNumber, err := strconv.Atoi(input)
		if err == nil && rangeNumber >= 1 && rangeNumber <= totalRanges {
			return rangeNumber
		}
		fmt.Println("Numero Inválido.")
	}
}

// promptSearchType prompts the user to select a search type
func promptSearchMode() int {
	reader := bufio.NewReader(os.Stdin)
	charReadline := '\n'

	if runtime.GOOS == "windows" {
		charReadline = '\r'
	}

	for {
		fmt.Print("Escolha o Modo de Busca (1 = Sequencial, 2 = Aleatório 3 = Aleatório + Sequencial): ")
		input, _ := reader.ReadString(byte(charReadline))
		input = strings.TrimSpace(input)
		searchMode, err := strconv.Atoi(input)
		if err == nil && (searchMode == 1 || searchMode == 2 || searchMode == 3) {
			return searchMode
		}
		fmt.Println("Modo de Busca Inválido.")
	}
}

func getRandomKeyInRange(minKeyInt, maxKeyInt *big.Int) *big.Int {
	rangeInt := new(big.Int).Sub(maxKeyInt, minKeyInt)
	randInt := new(big.Int).Rand(rand.New(rand.NewSource(time.Now().UnixNano())), rangeInt)
	randInt.Add(randInt, minKeyInt)
	return randInt
}

// saveTestedKeys saves the current private key state to a file with wallet number in the filename
func saveTestedKeys(privKeyInt *big.Int, walletNumber int) {
	filename := fmt.Sprintf("tested_keys_%d.txt", walletNumber)

	file, err := os.OpenFile(filename, os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0644)
	if err != nil {
		log.Fatalf("Failed to Open File: %v", err)
	}
	defer file.Close()

	privKeyHex := fmt.Sprintf("0x%s", privKeyInt.Text(16))
	_, err = file.WriteString(privKeyHex + "\n")
	if err != nil {
		log.Fatalf("Failed to Write to File: %v", err)
	}
}

func getInitialKeysChecked(fileName string) int {
	file, err := os.Open(fileName)
	if err != nil {
		fmt.Println("Error opening file:", err)
		return 0
	}
	defer file.Close()

	lineCount := 0
	scanner := bufio.NewScanner(file)
	for scanner.Scan() {
		lineCount++
	}

	if err := scanner.Err(); err != nil {
		fmt.Println("Error reading file:", err)
		return 0
	}

	return lineCount * 25000000
}

// saveTargetWallet saves the details of the found wallet to a file
func saveTargetWallet(address, privateKey string, balance float64) {
	filename := "target_wallet.txt"

	file, err := os.OpenFile(filename, os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0644)
	if err != nil {
		log.Fatalf("Failed to Open File: %v", err)
	}
	defer file.Close()

	data := fmt.Sprintf("Wallet Address: %s\nPrivate Key: %s\nBalance: %.12f BTC\n\n", address, privateKey, balance)
	_, err = file.WriteString(data)
	if err != nil {
		log.Fatalf("Failed to Write to File: %v", err)
	}
}

// Função para imprimir os resultados
func printResults(foundAddress *big.Int, walletAddress, privateKey string, balance float64, keysChecked int, startTime time.Time) {
	elapsedTime := time.Since(startTime).Seconds()
	keysPerSecond := float64(keysChecked) / elapsedTime
	color.White("=========================================================================\n")
	color.White("We Found the Target Wallet!!\n")
	color.Yellow("Private Key Hex: 0x%s\n", foundAddress.Text(16))
	color.Blue("Wallet Address: %s\n", walletAddress)
	color.Red("Private Key Wif: %s\n", privateKey)
	color.Green("Balance: %.12f BTC\n", balance)
	color.White("Keys: %s\n", humanize.Comma(int64(keysChecked)))
	color.White("Time: %.2f seconds\n", elapsedTime)
	color.White("Keys/Seg: %s\n", humanize.Comma(int64(keysPerSecond)))
	color.White("=========================================================================\n")
}

// checkBalance checks the balance of a Bitcoin address by querying blockchain.info
func checkBalance(address string) float64 {
	const retries = 2
	const delay = 3 * time.Second

	client := &http.Client{Timeout: 5 * time.Second}
	for attempt := 0; attempt < retries; attempt++ {
		resp, err := client.Get(fmt.Sprintf("https://blockchain.info/balance?active=%s", address))
		if err != nil {
			if attempt < retries-1 {
				log.Printf("Error Checking Balance, Retrying in %v: %v", delay, err)
				time.Sleep(delay)
				continue
			} else {
				log.Printf("Error Checking Balance: %v", err)
				return 0
			}
		}
		defer resp.Body.Close()

		if resp.StatusCode != http.StatusOK {
			log.Printf("Non-OK HTTP Status: %s", resp.Status)
			return 0
		}

		body, err := ioutil.ReadAll(resp.Body)
		if err != nil {
			log.Printf("Error Reading Response Body: %v", err)
			return 0
		}

		var result map[string]map[string]interface{}
		if err := json.Unmarshal(body, &result); err != nil {
			log.Printf("Error Unmarshalling JSON: %v", err)
			return 0
		}

		finalBalance := result[address]["final_balance"].(float64)
		return finalBalance / 100000000 // Convert from satoshis to bitcoins
	}
	return 0
}
