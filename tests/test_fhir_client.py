import pytest
from healthcare_agent.external.fhir_client import FHIRClient

class TestFHIRClient:
    @pytest.fixture
    def client(self):
        return FHIRClient(base_url="http://test-fhir.local", token="test-token")
    
    def test_client_initialization(self, client):
        assert client.base_url == "http://test-fhir.local"
        assert client.token == "test-token"
    
    def test_headers_generation(self, client):
        headers = client._headers()
        assert "Authorization" in headers
        assert headers["Authorization"] == "Bearer test-token"
        assert headers["Content-Type"] == "application/fhir+json"