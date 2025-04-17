import base64

def encrypt_card_number(card_number):
    """
    Encrypt a card number using base64 encoding.
    
    Args:
        card_number (str): The card number to encrypt
        
    Returns:
        str: The encrypted card number
    """
    if not card_number:
        return None
    
    # Remove any spaces from the card number
    card_number = card_number.replace(' ', '')
    
    # Convert the card number to bytes and encode with base64
    encoded_bytes = base64.b64encode(card_number.encode('utf-8'))
    
    # Convert the encoded bytes back to a string for storage
    return encoded_bytes.decode('utf-8')

def decrypt_card_number(encrypted_card_number):
    """
    Decrypt a card number that was encrypted using base64 encoding.
    
    Args:
        encrypted_card_number (str): The encrypted card number
        
    Returns:
        str: The decrypted card number
    """
    if not encrypted_card_number:
        return None
    
    try:
        # Convert the encrypted string to bytes and decode with base64
        decoded_bytes = base64.b64decode(encrypted_card_number.encode('utf-8'))
        
        # Convert the decoded bytes back to a string
        return decoded_bytes.decode('utf-8')
    except Exception as e:
        print(f"Error decrypting card number: {e}")
        return None

# Test with a sample card number
card_number = "4111111111111111"
print(f"Original card number: {card_number}")

# Encrypt the card number
encrypted = encrypt_card_number(card_number)
print(f"Encrypted card number: {encrypted}")

# Decrypt the card number
decrypted = decrypt_card_number(encrypted)
print(f"Decrypted card number: {decrypted}")

# Verify the decryption matches the original
if card_number == decrypted:
    print("SUCCESS: Original and decrypted values match")
else:
    print("FAILURE: Original and decrypted values do not match")
