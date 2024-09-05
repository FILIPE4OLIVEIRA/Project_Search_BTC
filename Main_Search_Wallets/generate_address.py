import mnemonic  # Importa o módulo mnemonic para geração de frases mnemônicas
import bip32utils  # Importa o módulo bip32utils para trabalhar com chaves BIP32

from bitcoinlib.keys import HDKey  # Importa HDKey da biblioteca bitcoinlib para gerar endereços Bitcoin
from bip32utils import BIP32_HARDEN  # Importa BIP32_HARDEN do bip32utils para trabalhar com chaves BIP32 endurecidas

# Função para gerar uma frase mnemônica
def generate_mnemonic():
    mnemo = mnemonic.Mnemonic("english") # Cria um objeto Mnemonic com o idioma inglês
    mnemonic_phrase = mnemo.generate(strength=256) # Gera uma frase mnemônica com 256 bits de força
    return mnemonic_phrase

# Função para gerar uma carteira bech32
def bench32_wallet(mnemonic_phrase):
    seed = mnemonic.Mnemonic.to_seed(mnemonic_phrase)  # Converte a frase mnemônica em uma semente
    root_key = bip32utils.BIP32Key.fromEntropy(seed)  # Cria uma chave BIP32 a partir da semente
    child_key = root_key.ChildKey(44 + BIP32_HARDEN).ChildKey(0 + BIP32_HARDEN).ChildKey(0 + BIP32_HARDEN).ChildKey(0).ChildKey(0)  # Deriva a chave filha
    private_key = child_key.WalletImportFormat()  # Obtém    o formato de importação da chave privada
    public_key_hex = child_key.PublicKey().hex()  # Obtém a chave pública em formato hexadecimal
    hdkey = HDKey(public_key_hex)  # Cria um objeto HDKey com a chave pública
    address = hdkey.address(encoding='bech32')  # Gera um endereço bech32
    return address, private_key  # Retorna a frase mnemônica, o endereço e a chave privada

# Função para gerar uma carteira segwit
def segwit_wallet(mnemonic_phrase):
    seed = mnemonic.Mnemonic.to_seed(mnemonic_phrase)  # Converte a frase mnemônica em uma semente
    root_key = bip32utils.BIP32Key.fromEntropy(seed)  # Cria uma chave BIP32 a partir da semente
    child_key = root_key.ChildKey(44 + BIP32_HARDEN).ChildKey(0 + BIP32_HARDEN).ChildKey(0 + BIP32_HARDEN).ChildKey(0).ChildKey(0)  # Deriva a chave filha
    address = child_key.P2WPKHoP2SHAddress()  # Gera um endereço P2WPKH sobre P2SH
    private_key = child_key.WalletImportFormat()  # Obtém o formato de importação da chave privada
    return address, private_key  # Retorna a frase mnemônica, o endereço e a chave privada

# Função para gerar uma carteira legacy
def legacy_wallet(mnemonic_phrase):
    seed = mnemonic.Mnemonic.to_seed(mnemonic_phrase)  # Converte a frase mnemônica em uma semente
    root_key = bip32utils.BIP32Key.fromEntropy(seed)  # Cria uma chave BIP32 a partir da semente
    child_key = root_key.ChildKey(44 + BIP32_HARDEN).ChildKey(0 + BIP32_HARDEN).ChildKey(0 + BIP32_HARDEN).ChildKey(0).ChildKey(0)  # Deriva a chave filha
    address = child_key.Address()  # Gera um endereço legacy
    private_key = child_key.WalletImportFormat()  # Obtém o formato de importação da chave privada
    return address, private_key  # Retorna a frase mnemônica, o endereço e a chave privada

def generate_all_wallets(mnemonic_phrase):
    # Converte a frase mnemônica em uma semente
    seed = mnemonic.Mnemonic.to_seed(mnemonic_phrase)
    # Cria a chave BIP32 a partir da semente
    root_key = bip32utils.BIP32Key.fromEntropy(seed)
    # Deriva a chave filha
    child_key = root_key.ChildKey(44 + BIP32_HARDEN).ChildKey(0 + BIP32_HARDEN).ChildKey(0 + BIP32_HARDEN).ChildKey(0).ChildKey(0)
    private_key = child_key.WalletImportFormat()  # Chave privada no formato WIF
    public_key_hex = child_key.PublicKey().hex()  # Chave pública em formato hexadecimal
    hdkey = HDKey(public_key_hex)  # Objeto HDKey com chave pública
   
    # Gerar carteira Bech32
    bech32_address = hdkey.address(encoding='bech32')  # Endereço Bech32
    # Gerar carteira SegWit (P2WPKH sobre P2SH)
    segwit_address = child_key.P2WPKHoP2SHAddress()  # Endereço SegWit
    # Gerar carteira Legacy
    legacy_address = child_key.Address()  # Endereço Legacy
    
    # Retornar os três tipos de endereços e suas respectivas chaves privadas
    return {
        "Bech32": {"bech32_address": bech32_address},
        "Segwit": {"segwit_address": segwit_address},
        "Legacy": {"legacy_address": legacy_address},
        "Private Key":{"private_key": private_key}
    }

def generate_puzzle_address(key):
    private_key_hex = hex(key)[2:].zfill(64)
    public_address = HDKey(private_key_hex).address()
    wif_private_key = HDKey(private_key_hex).wif_key()
    return public_address, wif_private_key
