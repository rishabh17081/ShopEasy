import base64

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

# Test decryption of the card numbers from the database
encrypted_card1 = "MzcxNDQ5NjM1Mzk4NDMx"
encrypted_card2 = "MzcxMjM0ODA2OTg3MDM0"

print("Decrypting card numbers from database:")
print(f"Card 1 (encrypted): {encrypted_card1}")
print(f"Card 1 (decrypted): {decrypt_card_number(encrypted_card1)}")
print(f"Card 2 (encrypted): {encrypted_card2}")
print(f"Card 2 (decrypted): {decrypt_card_number(encrypted_card2)}")
