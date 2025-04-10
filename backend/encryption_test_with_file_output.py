import base64
import os

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
        return f"Error decrypting card number: {e}"

# Create a file to write the test results
with open('encryption_test_results.txt', 'w') as f:
    # Test cases
    test_cases = [
        "4111111111111111",  # Visa
        "5555555555554444",  # Mastercard
        "378282246310005",   # American Express
        "6011111111111117",  # Discover
        "3530111333300000",  # JCB
    ]
    
    f.write("Card Encryption Test Results\n")
    f.write("==========================\n\n")
    
    for i, card_number in enumerate(test_cases):
        f.write(f"Test Case {i+1}: {card_number}\n")
        
        # Encrypt the card number
        encrypted = encrypt_card_number(card_number)
        f.write(f"Encrypted: {encrypted}\n")
        
        # Decrypt the card number
        decrypted = decrypt_card_number(encrypted)
        f.write(f"Decrypted: {decrypted}\n")
        
        # Verify the decryption matches the original
        if card_number == decrypted:
            f.write("✓ SUCCESS: Original and decrypted values match\n")
        else:
            f.write("✗ FAILURE: Original and decrypted values do not match\n")
        
        f.write("\n")
    
    f.write("Test Complete\n")

print("Test completed. Results written to encryption_test_results.txt")
