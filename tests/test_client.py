import pytest
from unittest.mock import Mock, patch
from dns_prove.client import main
from dns_prove.dnsprover import DnsProver
from dns_prove.crypto.initEth import verify_signed_text_record, generate_signature
from cryptography.hazmat.primitives.asymmetric import ec

# Test data
TEST_DOMAIN = "example.com"
TEST_ORACLE = "0x4B1488B7a6B320d2D721406204aBc3eeAa9AD329"
TEST_PROVIDER = "http://localhost:8545"

@pytest.fixture
def mock_dnsprover():
    with patch('dns_prove.client.DnsProver') as mock:
        yield mock

def test_cli_help(capsys):
    """Test help message"""
    with pytest.raises(SystemExit):
        main(['--help'])
    captured = capsys.readouterr()
    assert 'dns_prove' in captured.out
    assert 'oracle' in captured.out

def test_record_lookup(mock_dnsprover):
    """Test basic record lookup"""
    prover = mock_dnsprover.return_value
    prover.lookup.return_value = [{"name": TEST_DOMAIN, "type": "TXT"}]
    
    with patch('sys.argv', ['dns_prove', 'TXT', TEST_DOMAIN, '--oracle', TEST_ORACLE]):
        assert main() == 0
        prover.lookup.assert_called_once()

def test_invalid_arguments():
    """Test invalid argument handling"""
    with pytest.raises(SystemExit):
        with patch('sys.argv', ['dns_prove']):
            main()

def test_crypto_functions():
    """Test cryptographic functions"""
    private_key = ec.generate_private_key(ec.SECP256K1())
    message = "test message"
    signature = generate_signature(private_key, message)
    assert signature is not None 