from bitcoinlib.keys import HDKey

def generate_address(key):
    private_key_hex = hex(key)[2:].zfill(64)
    public_address = HDKey(private_key_hex).address()
    wif_private_key = HDKey(private_key_hex).wif_key()
    return public_address, wif_private_key
