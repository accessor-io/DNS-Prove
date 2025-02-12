import pytest
from pathlib import Path

def test_full_verification_flow(test_prover, test_cache, test_batch):
    """Test complete verification flow with all components"""
    # Test domain verification
    domain = "test.eth"
    proof = test_prover.construct_proof("TXT", domain)
    assert proof is not None
    
    # Test caching
    test_cache.set(domain, "TXT", proof)
    cached_proof = test_cache.get(domain, "TXT")
    assert cached_proof == proof
    
    # Test batch processing
    test_file = Path("test_domains.txt")
    test_file.write_text("test1.eth\ntest2.eth")
    
    results = test_batch.process_file(str(test_file))
    assert len(results) == 2
    assert all(r["status"] in ["success", "cached"] for r in results)
    
    # Cleanup
    test_file.unlink()

def test_network_switching(test_prover):
    """Test network switching functionality"""
    # Test mainnet
    assert test_prover.network == "mainnet"
    
    # Switch to testnet
    test_prover = DnsProver(network="testnet")
    assert test_prover.network == "testnet"
    assert "sepolia" in test_prover.provider_url.lower() 