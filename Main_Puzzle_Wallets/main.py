from target_address import target_address_legacy
from search_functions import *

if __name__ == "__main__":
    TARGET_ADDRESSES = target_address_legacy
    
    user_choice = int(input("Enter Wallet Target (1-161): "))
    min_key, max_key = search_range(user_choice)
    
    search_method = int(input(
        "[1] Sequential\n"
        "[2] Random\n"
        "[3] Sequential + Random\n"
        "Choose Search Method: "
    ))
    
    if search_method == 1:
        search_addresses_sequential(min_key, max_key, TARGET_ADDRESSES)
    elif search_method == 2:
        search_addresses_random(min_key, max_key, TARGET_ADDRESSES)
    elif search_method == 3:
        search_addresses_sequential_random(min_key, max_key, TARGET_ADDRESSES)
    else:
        print("Error: Número Invalido")

