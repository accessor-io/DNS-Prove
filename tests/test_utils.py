import unittest
from dns_prove.utils import build_proof, construct_rrsig, construct_rrset, hash_data

class TestUtils(unittest.TestCase):
    def test_build_proof(self):
        """Test building a DNS proof"""
        name = "example.com"
        rrsig = {
            "name": name,
            "type": "RRSIG",
            "ttl": 300,
            "algorithm": 13,
            "key": "test_key",
            "signature": "test_signature"
        }
        rrset = {
            "name": name,
            "type": "A",
            "ttl": 300,
            "data": "1.2.3.4"
        }

        proof = build_proof(name, rrsig, rrset)
        
        self.assertIsNotNone(proof)
        self.assertEqual(proof["name"], name)
        self.assertEqual(proof["rrsig"], rrsig)
        self.assertEqual(proof["rrset"], rrset)

    def test_construct_rrsig(self):
        """Test constructing an RRSIG record"""
        name = "example.com"
        record_type = "A"
        ttl = 300
        algorithm = 13
        key = "test_key"
        signature = "test_signature"

        rrsig = construct_rrsig(name, record_type, ttl, algorithm, key, signature)
        
        self.assertIsNotNone(rrsig)
        self.assertEqual(rrsig["name"], name)
        self.assertEqual(rrsig["type"], "RRSIG")
        self.assertEqual(rrsig["ttl"], ttl)
        self.assertEqual(rrsig["data"]["algorithm"], algorithm)
        self.assertEqual(rrsig["data"]["key"], key)
        self.assertEqual(rrsig["data"]["signature"], signature)

    def test_construct_rrset(self):
        """Test constructing an RRset record"""
        name = "example.com"
        record_type = "A"
        ttl = 300
        flags = 256
        algorithm = 13
        key = "test_key"

        rrset = construct_rrset(name, record_type, ttl, flags, algorithm, key)
        
        self.assertIsNotNone(rrset)
        self.assertEqual(rrset["name"], name)
        self.assertEqual(rrset["type"], record_type)
        self.assertEqual(rrset["ttl"], ttl)
        self.assertEqual(rrset["data"]["flags"], flags)
        self.assertEqual(rrset["data"]["algorithm"], algorithm)
        self.assertEqual(rrset["data"]["key"], key)

    def test_hash_data(self):
        """Test data hashing"""
        test_data = "test data"
        hash_result = hash_data(test_data)
        
        self.assertIsNotNone(hash_result)
        self.assertIsInstance(hash_result, bytes)
        self.assertEqual(len(hash_result), 32)  # SHA256 hash is 32 bytes

if __name__ == '__main__':
    unittest.main()
