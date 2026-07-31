from cryptography.fernet import Fernet

KEY = b'kFvgyyqnNT3a54R7uhhru1aUAMLKNPQr9yH4IhLYLn4='
cipher = Fernet(KEY)

def encrypt_card(card_number):
    return cipher.encrypt(card_number.encode()).decode()

def decrypt_card(encrypted_card):
    return cipher.decrypt(encrypted_card.encode()).decode()