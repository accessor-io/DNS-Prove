import pytest
from web3 import Web3
from unittest.mock import Mock, patch
from eth_abi.abi import encode
from dns_prove.dnsprover import DnsProver
from dns_prove.cache import ProofCache
from dns_prove.config import Config
from dns_prove.batch import BatchProcessor
from fastapi.testclient import TestClient
from dns_prove.api import app

@pytest.fixture
def web3_provider():
    return Web3.HTTPProvider("https://sepolia.infura.io/v3/YOUR_INFURA_PROJECT_ID")

@pytest.fixture
def oracle_address():
    return "0x742d35Cc6634C0532925a3b844Bc454e4438f44e"

@pytest.fixture
def test_domain():
    return "example.com"

@pytest.fixture
def test_eth_address():
    return "0x742d35Cc6634C0532925a3b844Bc454e4438f44e"

@pytest.fixture
def mock_web3():
    with patch('web3.Web3', autospec=True) as mock:
        mock.to_checksum_address = Web3.to_checksum_address
        mock.to_bytes = Web3.to_bytes
        mock.keccak = Web3.keccak
        mock.eth.abi.encode = encode
        yield mock

@pytest.fixture
def mock_dns_resolver():
    with patch('dns.resolver.Resolver', autospec=True) as mock:
        mock_answer = Mock()
        mock_answer.to_text.return_value = "0x742d35Cc6634C0532925a3b844Bc454e4438f44e"
        mock.resolve.return_value = [mock_answer]
        yield mock

@pytest.fixture
def test_prover(mock_web3, mock_dns_resolver):
    return DnsProver()

@pytest.fixture
def test_cache(tmp_path):
    return ProofCache(cache_dir=tmp_path / ".cache")

@pytest.fixture
def test_config(tmp_path):
    config_file = tmp_path / "config.yml"
    return Config(config_file=config_file)

@pytest.fixture
def test_batch(test_prover, test_cache):
    return BatchProcessor(test_prover, cache_enabled=True)

@pytest.fixture
def api_client():
    return TestClient(app)

@pytest.fixture
def provider_url():
    """Test provider URL"""
    return "https://mainnet.infura.io/v3/test-project-id" 