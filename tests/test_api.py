from fastapi.testclient import TestClient
import json

def test_verify_endpoint(api_client):
    """Test domain verification endpoint"""
    response = api_client.post(
        "/verify",
        json={
            "domain": "test.eth",
            "record_type": "TXT",
            "check_ens": True
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "proof" in data

def test_batch_endpoint(api_client):
    """Test batch processing endpoint"""
    response = api_client.post(
        "/batch",
        json={
            "domains": ["test1.eth", "test2.eth"],
            "record_type": "TXT",
            "parallel": True
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert all("status" in r for r in data)

def test_rate_limiting(api_client):
    """Test API rate limiting"""
    # Make multiple requests quickly
    responses = []
    for _ in range(105):  # Over the 100/minute limit
        response = api_client.post(
            "/verify",
            json={"domain": "test.eth"}
        )
        responses.append(response)
    
    # Check that some requests were rate limited
    assert any(r.status_code == 429 for r in responses) 