import os

def get_project_path():
    return os.path.dirname(os.path.abspath(__file__))

def record_wallet_data(wallet_count, mnemonic_phrase, address, private_key, balance):
    formatted_balance = f"{balance:.12f}"
    project_path = get_project_path()   # Obtém o diretório onde o script está localizado
    file_path = os.path.join(project_path, "target_address_found.txt")  # Define o caminho do arquivo no diretório do script
    mode = 'a' if os.path.exists(file_path) else 'w'  # Define o modo de abertura do arquivo
    with open(file_path, mode) as f:  # Abre o arquivo para escrita
        f.write(f"Wallet[{wallet_count}]\n")  # Escreve o número da carteira
        f.write(f"Mnemonic Phrase: {mnemonic_phrase}\n")  # Escreve a frase mnemônica
        f.write(f"Wallet Address: {address}\n")  # Escreve o endereço da carteira
        f.write(f"Wallet Private Key: {private_key}\n")  # Escreve a chave privada
        f.write(f"Wallet Balance: {formatted_balance}\n\n")  # Escreve o balance

def record_puzzle_data(wallet_count, min_key, max_key, public_address, private_key, private_key_hex, balance):
    project_path = get_project_path()  # Obtém o caminho do diretório do projeto
    file_path = os.path.join(project_path, "target_address_found.txt")  # Define o caminho da pasta de destino
    mode = 'a' if os.path.exists(file_path) else 'w'  # Define o modo de abertura do arquivo
    with open(file_path, mode) as f:  # Abre o arquivo para escrita
        f.write(f"Wallet[{wallet_count}]\n")
        f.write(f"Range[{hex(min_key)}:{hex(max_key)}]\n")
        f.write(f"Wallet Address: {public_address}\n")  # Escreve o endereço da carteira
        f.write(f"Wallet Private Key: {private_key}\n")  # Escreve a chave privada
        f.write(f"Wallet Hex Key: {private_key_hex}\n")
        f.write(f"Balance: {'%.12f' % balance}\n\n")

def record_last_key(private_key_hex):
    project_path = get_project_path()  # Obtém o caminho do diretório do projeto
    file_path = os.path.join(project_path, "last_key.txt")  # Define o caminho da pasta de destino
    mode = 'a' if os.path.exists(file_path) else 'w'  # Define o modo de abertura do arquivo
    with open(file_path, mode) as f:  # Abre o arquivo para escrita
        f.write(f"{private_key_hex}\n")
