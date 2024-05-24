import unittest
from dnssec_proof.dnsprover import DnsProver

class TestDnsProver(unittest.TestCase):
    def setUp(self):
        self.prover = DnsProver()

    def test_lookup(self):
        result = self.prover.lookup('DNSKEY', 'example.com')
        self.assertIsInstance(result, list)
        self.assertGreater(len(result), 0)

if __name__ == '__main__':
    unittest.main()
