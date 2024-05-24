import unittest
from dnssec_proof.utils import build_proof, construct_rrsig, construct_rrset

class TestUtils(unittest.TestCase):
    def test_build_proof(self):
        name = "."
        rrsig = {}
        rrset = []
        proof = build_proof(name, rrsig, rrset)
        self.assertEqual(proof["name"], name)
        self.assertEqual(proof["rrsig"], rrsig)
        self.assertEqual(proof["rrset"], rrset)

    def test_construct_rrsig(self):
        rrsig = construct_rrsig('.', 'RRSIG', 3600, 253, 'key', 'signature')
        self.assertEqual(rrsig['name'], '.')
        self.assertEqual(rrsig['type'], 'RRSIG')
        self.assertEqual(rrsig['data']['algorithm'], 253)

    def test_construct_rrset(self):
        rrset = construct_rrset('.', 'DNSKEY', 3600, 257, 253, 'key')
        self.assertEqual(rrset['name'], '.')
        self.assertEqual(rrset['type'], 'DNSKEY')
        self.assertEqual(rrset['data']['algorithm'], 253)

if __name__ == '__main__':
    unittest.main()
