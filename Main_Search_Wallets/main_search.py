import logging

from search_functions import *
from target_address import *
from record_data import *

def main_search_start():
    # Configura o registro de log 
    logging.basicConfig(level=logging.INFO, format='%(message)s')
    
    search_method = int(input(
        "[1] Search Puzlle Method\n"
        "[2] Search Know Wallet Method\n"
        "[3] Search Balance Method\n"
        "Choose Search Method: "
    ))
    
    
    if search_method == 1: 
        TARGET_PUZZLE_ADDRESSES = target_puzzle_address
        user_choice = int(input("Enter Wallet Target (1-161): "))
        min_key, max_key = search_range(user_choice)

        search_puzzle_method = int(input(
            "[1] Sequential\n"
            "[2] Random\n"
            "[3] Sequential + Random\n"
            "Choose Search Method: "
        ))
        
        if search_puzzle_method == 1:
            search_addresses_sequential(min_key, max_key, TARGET_PUZZLE_ADDRESSES)
        elif search_puzzle_method == 2:
            search_addresses_random(min_key, max_key, TARGET_PUZZLE_ADDRESSES)
        elif search_puzzle_method == 3:
            step_choice = int(input("Range Sequencial: "))
            if step_choice > 0:
                search_addresses_sequential_random(min_key, max_key, TARGET_PUZZLE_ADDRESSES, step_choice)
            else:
                search_addresses_sequential_random(min_key, max_key, TARGET_PUZZLE_ADDRESSES)
        else:
            print("Error: Número Invalido")
    elif search_method == 2:
        TARGET_KNOW_ADDRESSES = target_know_address
        search_know_wallet(TARGET_KNOW_ADDRESSES)
    elif search_method == 3:
        search_non_zero_wallet()
      
    logging.info(rainbow.green_console("Processo Bem-Sucedido e Finalizado."))

if __name__ == "__main__":
    main_search_start()
