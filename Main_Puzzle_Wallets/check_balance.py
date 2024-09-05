import time # Importa o módulo time
import logging  # Importa o módulo logging para registro de log
import requests # Importa o módulo requests para acesso de api
   
# Função para verificar o saldo de um endereço Bitcoin
def check_balance(address, retries=2, delay=3):
    # Configura o registro de log 
    logging.basicConfig(level=logging.INFO, format='%(message)s')
    for attempt in range(retries):  # Tenta verificar o saldo o número de vezes especificado por retries
        try:
            # Faz uma requisição HTTP GET para obter o saldo do endereço
            response = requests.get(f"https://blockchain.info/balance?active={address}", timeout=5)
            response.raise_for_status()  # Levanta uma exceção se a requisição não foi bem-sucedida
            data = response.json()  # Converte a resposta em formato JSON
            balance = data[address]["final_balance"]  # Obtém o saldo final do endereço
            return balance / 100000000  # Converte o saldo de satoshis para bitcoins
        except requests.RequestException as e:  # Captura exceções relacionadas à requisição
            if attempt < retries - 1:  # Se ainda há tentativas restantes
                logging.error(f"Error Checking Balance, Retrying in {delay} Seconds: {str(e)}")  # Loga o erro e espera um tempo antes de tentar novamente
                time.sleep(delay)  # Espera pelo tempo especificado antes de tentar novamente
            else:
                logging.error("Error Checking Balance: %s", str(e))  # Loga o erro se não há mais tentativas restantes
    return 0  # Retorna saldo zero se todas as tentativas falharem
