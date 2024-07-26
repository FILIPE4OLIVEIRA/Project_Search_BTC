import rainbow
import random

from record_data import record_data, record_last_key
from check_balance import check_balance
from target_ranges import target_ranges
from generate_address import generate_address

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
        public_address, private_key = generate_address(key)    
        
        wallet_count += 1
        private_key_hex = hex(key) 
        if wallet_count % 1000 == 0:
            print(f"[{rainbow.yellow_console(wallet_count)}]"\
                    f" Public Address: {rainbow.blue_console(public_address)}"\
                    f" Private Key: {rainbow.dark_red_console(private_key)}")
            record_last_key(private_key_hex)
        
        if public_address in target_addresses:
            balance = check_balance(public_address)
            print_wallet_info(wallet_count, min_key, max_key, public_address, private_key, private_key_hex, balance)
            record_data(wallet_count, min_key, max_key, public_address, private_key, private_key_hex, balance)
            break
        
        key += 1
        
def search_addresses_random(min_key, max_key, target_addresses):
    wallet_count = 0
    while True:
        key = random.randint(min_key, max_key)
        public_address, private_key = generate_address(key)
        
        wallet_count += 1
        private_key_hex = hex(key)
        
        if wallet_count % 1000 == 0:
            print(f"[{rainbow.yellow_console(wallet_count)}]"
                  f" Public Address: {rainbow.blue_console(public_address)}"
                  f" Private Key: {rainbow.dark_red_console(private_key)}")
            record_last_key(private_key_hex)
        
        if public_address in target_addresses:
            balance = check_balance(public_address)
            print_wallet_info(wallet_count, min_key, max_key, public_address, private_key, private_key_hex, balance)
            record_data(wallet_count, min_key, max_key, public_address, private_key, private_key_hex, balance)
            break
        
def search_addresses_sequential_random(min_key, max_key, target_addresses, step=1000000):
    wallet_count = 0
    key = random.randint(min_key, max_key)
    
    while True:
        # Avança sequencialmente por `step` chaves
        end_key = min(key + step, max_key)
        while key <= end_key:
            public_address, private_key = generate_address(key)
            
            wallet_count += 1
            private_key_hex = hex(key)
            
            if wallet_count % 1000 == 0:
                print(f"[{rainbow.yellow_console(wallet_count)}]"
                      f" Public Address: {rainbow.blue_console(public_address)}"
                      f" Private Key: {rainbow.dark_red_console(private_key)}")
                record_last_key(private_key_hex)
            
            if public_address in target_addresses:
                balance = check_balance(public_address)
                print_wallet_info(wallet_count, min_key, max_key, public_address, private_key, private_key_hex, balance)
                record_data(wallet_count, min_key, max_key, public_address, private_key, private_key_hex, balance)
                return
            
            key += 1
        
        # Sorteia uma nova chave aleatória para continuar a busca
        key = random.randint(min_key, max_key)

