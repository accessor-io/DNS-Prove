import unittest
from dnssec_proof.dnsprover import DnsProver

class TestDnsProver(unittest.TestCase):
    def setUp(self):
        self.dnsprover = DnsProver()

    def test_lookup_and_submit(self):
        # Add test cases for lookup_and_submit method
        pass

if __name__ == '__main__':
    unittest.main()
