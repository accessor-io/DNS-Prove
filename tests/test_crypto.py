import unittest
from dns_prove.crypto.initEth import verify_signed_text_record
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization

class TestCrypto(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures"""
        # Generate a test key pair
        self.private_key = ec.generate_private_key(ec.SECP256K1())
        self.public_key = self.private_key.public_key()

    def test_verify_signed_text_record(self):
        """Test verification of signed DNS TXT records"""
        # Create a test signature
        signature = b"test_signature"
        message = "test_message"
        
        # Test with valid signature format
        txt_record = f"v=ethereum-proof signature={signature.hex()}"
        result = verify_signed_text_record(txt_record, self.public_key)
        self.assertIsInstance(result, bool)
        
        # Test with invalid signature format
        invalid_txt_record = "v=ethereum-proof signature=invalid"
        result = verify_signed_text_record(invalid_txt_record, self.public_key)
        self.assertFalse(result)

    def test_invalid_inputs(self):
        """Test handling of invalid inputs"""
        # Test with None values
        result = verify_signed_text_record(None, self.public_key)
        self.assertFalse(result)
        
        # Test with empty values
        result = verify_signed_text_record("", self.public_key)
        self.assertFalse(result)
        
        # Test with invalid record format
        result = verify_signed_text_record("invalid_record", self.public_key)
        self.assertFalse(result)

    def test_proof_encoding(self):
        """Test proof data encoding"""
        proof_data = {
            'rrset': b'test_rrset',
            'sig': b'test_sig'
        }
        
        encoded = self.test_prover._encode_proof(proof_data)
        self.assertIsInstance(encoded, bytes)
        self.assertGreater(len(encoded), 0)

if __name__ == '__main__':
    unittest.main() 