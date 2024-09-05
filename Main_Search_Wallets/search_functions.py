import os
import logging
import rainbow
import random

from record_data import  *
from check_balance import *
from target_address import *
from target_ranges import *
from generate_address import *

def print_wallet_info(wallet_count, min_key, max_key, public_address, private_key, private_key_hex, balance):
    print(rainbow.dark_green_console("We Found the Target Wallet!!"))
    print(f"Wallet [{rainbow.yellow_console(wallet_count)}]")
    print(f"Range:{rainbow.cyan_console(hex(min_key))},{rainbow.cyan_console(hex(max_key))}")
    print(f"Public Address: {rainbow.blue_console(public_address)}")
    print(f"Private Key: {rainbow.dark_red_console(private_key)}")
    print(f"Hex Key: {rainbow.dark_red_console(private_key_hex)}")
    print(f"Balance: {rainbow.green_console('%.12f' % balance)}")

def search_range(user_choice):
    if user_choice >= 1 or user_choice < len(target_ranges)+1:
        chosen_range = target_ranges[user_choice-1]
        min_value = int(chosen_range["min"], 16)
        max_value = int(chosen_range["max"], 16)
        return min_value, max_value
    else:
        raise ValueError("Error: Número Invalido")

def search_addresses_sequential(min_key, max_key, target_addresses):   
    wallet_count = 0
    key = min_key
    while key <= max_key:
        public_address, private_key = generate_puzzle_address(key)    
        
        wallet_count += 1
        private_key_hex = hex(key) 
        if wallet_count % 1000 == 0:
            print(f"[{rainbow.yellow_console(wallet_count)}]"\
                    f" Public Address: {rainbow.blue_console(public_address)}"\
                    f" Current Key: {rainbow.red_console(private_key_hex)}")
            record_last_key(private_key_hex)
        
        if public_address in target_addresses:
            balance = check_balance(public_address)
            print_wallet_info(wallet_count, min_key, max_key, public_address, private_key, private_key_hex, balance)
            record_puzzle_data(wallet_count, min_key, max_key, public_address, private_key, private_key_hex, balance)
            break
        
        key += 1
        
    print(f"{rainbow.dark_red_console('No Found Wallet in this Range')}")
        
def search_addresses_random(min_key, max_key, target_addresses):
    wallet_count = 0
    while True:
        key = random.randint(min_key, max_key)
        public_address, private_key = generate_puzzle_address(key)
        
        wallet_count += 1
        private_key_hex = hex(key)
        
        if wallet_count % 1000 == 0:
            print(f"[{rainbow.yellow_console(wallet_count)}]"
                  f" Public Address: {rainbow.blue_console(public_address)}"
                  f" Current Key: {rainbow.red_console(private_key_hex)}")
            record_last_key(private_key_hex)
        
        if public_address in target_addresses:
            balance = check_balance(public_address)
            print_wallet_info(wallet_count, min_key, max_key, public_address, private_key, private_key_hex, balance)
            record_puzzle_data(wallet_count, min_key, max_key, public_address, private_key, private_key_hex, balance)
            break
        
def search_addresses_sequential_random(min_key, max_key, target_addresses, step = 2500000):
    wallet_count = 0
    key = random.randint(min_key, max_key)
    
    while True:
        # Avança sequencialmente por `step` chaves
        end_key = min(key + step, max_key)
        while key <= end_key:
            public_address, private_key = generate_puzzle_address(key)
            
            wallet_count += 1
            private_key_hex = hex(key)
            
            if wallet_count % 1000 == 0:
                print(f"[{rainbow.yellow_console(wallet_count)}]"
                      f" Public Address: {rainbow.blue_console(public_address)}"
                      f" Current Key: {rainbow.red_console(private_key_hex)}")
                record_last_key(private_key_hex)
            
            if public_address in target_addresses:
                balance = check_balance(public_address)
                print_wallet_info(wallet_count, min_key, max_key, public_address, private_key, private_key_hex, balance)
                record_puzzle_data(wallet_count, min_key, max_key, public_address, private_key, private_key_hex, balance)
                return
            
            key += 1
            
        key = random.randint(min_key, max_key)
        
def search_non_zero_wallet():    
    wallet_count = 0  # Inicializa o contador de carteiras
    while True:  # Loop infinito para gerar carteiras
        wallet_count += 1  # Incrementa o contador de carteiras
        mnemonic_phrase = generate_mnemonic()  # Gera uma nova frase mnemônica
        address, private_key = legacy_wallet(mnemonic_phrase)  # Gera uma nova carteira
        # address, private_key = segwit_wallet(mnemonic_phrase)  # Gera uma nova carteira
        # address, private_key = bench32_wallet(mnemonic_phrase)  # Gera uma nova carteira
        
        # APENAS PRA TESTE
        # if wallet_count == 20:
        #     address = "13zb1hQbWVsc2S7ZTZnP2G4undNNpdh5so"
        
        balance = check_balance(address)
         
        if balance == 0:
            balance_color = rainbow.yellow_console('%.12f' % balance)  # Colore o saldo de amarelo se for zero
        else:
            balance_color = rainbow.green_console('%.12f' % balance)  # Colore o saldo de verde se for maior que zero
        
        # Registra os detalhes da carteira gerada
        if wallet_count % 2 == 0:
            logging.info(f"Wallet Nº [{wallet_count}] {rainbow.gray_console('Wallet Address:')} {rainbow.blue_console(address)} {rainbow.gray_console('Wallet Balance:')} {balance_color}")
        
        if balance >= 0.01:  # Verifica se o saldo é maior ou igual a 0.001 BTC
            logging.info(f"{rainbow.yellow_console('We Found a Wallet with Non-Zero Balance')} {rainbow.green_console(balance)} BTC")
            record_wallet_data(wallet_count, mnemonic_phrase, address, private_key, balance)  # Grava os dados da carteira
            break  # Encerra o loop  

def search_know_wallet(target_know_address):
    wallet_count = 0  # Inicializa o contador de carteiras
    while True:
        wallet_count += 1  # Incrementa o contador de carteiras
        mnemonic_phrase = generate_mnemonic()  # Gera uma nova frase mnemônica
        wallets = generate_all_wallets(mnemonic_phrase)  # Gera as três carteiras (Bech32, SegWit, Legacy)
    
        # APENAS PRA TESTE
        # if wallet_count == 20:
        #     wallets['Legacy']['legacy_address'] = "bc1q5nfww5jn5k4ghg7dpa4gy85x7uu3l4g0m0re76"
        
        # Registra os detalhes da carteira (Bech32, SegWit e Legacy)
        if wallet_count % 100 == 0:
            os.system('cls')
            logging.info(f"Wallet Nº [{wallet_count}]"
                        f"\n {rainbow.gray_console('Bech32 Address:')} {rainbow.blue_console(wallets['Bech32']['bech32_address'])}"
                        f"\n {rainbow.gray_console('SegWit Address:')} {rainbow.blue_console(wallets['Segwit']['segwit_address'])}"
                        f"\n {rainbow.gray_console('Legacy Address:')} {rainbow.blue_console(wallets['Legacy']['legacy_address'])} "
                        f"\n {rainbow.gray_console('Private Key (WIF):')} {rainbow.red_console(wallets['Private Key']['private_key'])}")

        for wallet_type in ['Bech32', 'Segwit', 'Legacy']:
            address_key = f"{wallet_type.lower()}_address"  # Acessa o endereço correto baseado no tipo de carteira
            address = wallets[wallet_type][address_key]
            private_key = wallets['Private Key']['private_key']
            
            if address in target_know_address:
                os.system('cls')
                balance = check_balance(address)
                formatted_balance = f"{balance:.12f}"
                logging.info(f"{rainbow.yellow_console('We Found the Target Wallet!')}"
                             f"\n{rainbow.gray_console('Wallet Nº')} [{wallet_count}]"
                             f"\n{rainbow.gray_console('Wallet Address:')} {rainbow.blue_console(address)}"
                             f"\n{rainbow.gray_console('Private Key (WIF):')} {rainbow.red_console(private_key)}"
                             f"\n{rainbow.gray_console('Wallet Balance:')} {rainbow.cyan_console(formatted_balance)}")
                
                # Grava os dados da carteira
                record_wallet_data(wallet_count, mnemonic_phrase, address, private_key, balance)
                return

