import pytest
from web3 import Web3
from unittest.mock import Mock

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
    """Fixture to provide a mocked Web3 instance"""
    mock = Mock()
    mock.eth.chain_id = 1  # Mainnet
    mock.eth.contract = Mock()
    return mock

@pytest.fixture
def mock_dns_resolver():
    """Fixture to provide a mocked DNS resolver"""
    mock = Mock()
    mock.resolve.return_value = [Mock(to_text=lambda: "192.168.1.1")]
    return mock

@pytest.fixture
def provider_url():
    """Test provider URL"""
    return "https://mainnet.infura.io/v3/test-project-id" 