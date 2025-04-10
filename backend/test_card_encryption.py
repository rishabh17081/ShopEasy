import sys
import os
import base64

# Add the current directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the encryption functions
from app.utils.encryption import encrypt_card_number, decrypt_card_number

def test_encryption_decryption():
    """Test the encryption and decryption of card numbers"""
    
    # Test cases
    test_cases = [
        "4111111111111111",  # Visa
        "5555555555554444",  # Mastercard
        "378282246310005",   # American Express
        "6011111111111117",  # Discover
        "3530111333300000",  # JCB
        "",                  # Empty string
        None                 # None value
    ]
    
    print("Testing card number encryption and decryption:")
    print("-" * 50)
    
    for i, card_number in enumerate(test_cases):
        print(f"\nTest Case {i+1}: {card_number if card_number else 'None'}")
        
        # Encrypt the card number
        encrypted = encrypt_card_number(card_number)
        print(f"Encrypted: {encrypted}")
        
        # Decrypt the card number
        decrypted = decrypt_card_number(encrypted)
        print(f"Decrypted: {decrypted}")
        
        # Verify the decryption matches the original
        if card_number == decrypted:
            print("✅ SUCCESS: Original and decrypted values match")
        else:
            print("❌ FAILURE: Original and decrypted values do not match")
            print(f"  Original: {card_number}")
            print(f"  Decrypted: {decrypted}")
    
    print("\n" + "-" * 50)
    print("Encryption/Decryption Test Complete")

def test_manual_base64():
    """Test manual base64 encoding and decoding to verify the implementation"""
    
    card_number = "4111111111111111"
    print(f"\nManual Base64 Test with: {card_number}")
    
    # Manual base64 encoding
    encoded_bytes = base64.b64encode(card_number.encode('utf-8'))
    encoded_str = encoded_bytes.decode('utf-8')
    print(f"Manual Base64 Encoded: {encoded_str}")
    
    # Manual base64 decoding
    decoded_bytes = base64.b64decode(encoded_str.encode('utf-8'))
    decoded_str = decoded_bytes.decode('utf-8')
    print(f"Manual Base64 Decoded: {decoded_str}")
    
    # Verify
    if card_number == decoded_str:
        print("✅ SUCCESS: Manual base64 encoding/decoding works correctly")
    else:
        print("❌ FAILURE: Manual base64 encoding/decoding failed")

if __name__ == "__main__":
    test_encryption_decryption()
    test_manual_base64()
