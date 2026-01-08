"""Tests for Frappe API client."""

import json
from pathlib import Path

import pytest
import responses
from requests.exceptions import ConnectionError, Timeout

from frappecli.client import FrappeClient, FrappeAPIError, FrappeConnectionError


@pytest.fixture
def api_responses():
    """Load API response fixtures."""
    fixtures_path = Path(__file__).parent / "fixtures" / "api_responses.json"
    with fixtures_path.open() as f:
        return json.load(f)


@pytest.fixture
def client():
    """Create a test client."""
    return FrappeClient(
        base_url="https://test.example.com",
        api_key="test_key",
        api_secret="test_secret",
    )


class TestClientInitialization:
    """Test client initialization."""

    def test_client_init(self):
        """Test client initialization with credentials."""
        client = FrappeClient(
            base_url="https://example.com",
            api_key="my_key",
            api_secret="my_secret",
        )
        assert client.base_url == "https://example.com"
        assert client.session.headers["Authorization"] == "token my_key:my_secret"

    def test_client_strips_trailing_slash(self):
        """Test that trailing slash is removed from base URL."""
        client = FrappeClient(
            base_url="https://example.com/",
            api_key="key",
            api_secret="secret",
        )
        assert client.base_url == "https://example.com"

    def test_client_default_headers(self, client):
        """Test that default headers are set."""
        assert "Authorization" in client.session.headers
        assert "Content-Type" in client.session.headers
        assert client.session.headers["Content-Type"] == "application/json"


class TestHTTPMethods:
    """Test HTTP methods."""

    @responses.activate
    def test_get_request(self, client, api_responses):
        """Test GET request."""
        responses.add(
            responses.GET,
            "https://test.example.com/api/resource/User/test@example.com",
            json=api_responses["success_response"],
            status=200,
        )

        result = client.get("/api/resource/User/test@example.com")
        assert result == api_responses["success_response"]["message"]

    @responses.activate
    def test_post_request(self, client, api_responses):
        """Test POST request."""
        responses.add(
            responses.POST,
            "https://test.example.com/api/resource/User",
            json=api_responses["success_response"],
            status=200,
        )

        result = client.post("/api/resource/User", data={"email": "new@example.com"})
        assert result == api_responses["success_response"]["message"]

    @responses.activate
    def test_put_request(self, client, api_responses):
        """Test PUT request."""
        responses.add(
            responses.PUT,
            "https://test.example.com/api/resource/User/test@example.com",
            json=api_responses["success_response"],
            status=200,
        )

        result = client.put(
            "/api/resource/User/test@example.com", data={"enabled": 0}
        )
        assert result == api_responses["success_response"]["message"]

    @responses.activate
    def test_delete_request(self, client):
        """Test DELETE request."""
        responses.add(
            responses.DELETE,
            "https://test.example.com/api/resource/User/test@example.com",
            json={"message": "ok"},
            status=202,
        )

        result = client.delete("/api/resource/User/test@example.com")
        assert result == "ok"


class TestResponseParsing:
    """Test response parsing."""

    @responses.activate
    def test_extract_message_field(self, client, api_responses):
        """Test extraction of message field from response."""
        responses.add(
            responses.GET,
            "https://test.example.com/api/test",
            json=api_responses["success_response"],
            status=200,
        )

        result = client.get("/api/test")
        assert result == api_responses["success_response"]["message"]

    @responses.activate
    def test_list_response(self, client, api_responses):
        """Test handling of list responses."""
        responses.add(
            responses.GET,
            "https://test.example.com/api/resource/User",
            json=api_responses["list_response"],
            status=200,
        )

        result = client.get("/api/resource/User")
        assert isinstance(result, list)
        assert len(result) == 3


class TestErrorHandling:
    """Test error handling."""

    @responses.activate
    def test_404_error(self, client, api_responses):
        """Test 404 error handling."""
        responses.add(
            responses.GET,
            "https://test.example.com/api/resource/User/notfound",
            json=api_responses["error_404"],
            status=404,
        )

        with pytest.raises(FrappeAPIError, match="404.*Document not found"):
            client.get("/api/resource/User/notfound")

    @responses.activate
    def test_403_error(self, client, api_responses):
        """Test 403 error handling."""
        responses.add(
            responses.GET,
            "https://test.example.com/api/resource/User/test",
            json=api_responses["error_403"],
            status=403,
        )

        with pytest.raises(FrappeAPIError, match="403.*Not permitted"):
            client.get("/api/resource/User/test")

    @responses.activate
    def test_500_error(self, client, api_responses):
        """Test 500 error handling."""
        responses.add(
            responses.GET,
            "https://test.example.com/api/test",
            json=api_responses["error_500"],
            status=500,
        )

        with pytest.raises(FrappeAPIError, match="500"):
            client.get("/api/test")

    @responses.activate
    def test_connection_error(self, client):
        """Test connection error handling."""
        responses.add(
            responses.GET,
            "https://test.example.com/api/test",
            body=ConnectionError("Connection refused"),
        )

        with pytest.raises(FrappeConnectionError, match="Failed to connect"):
            client.get("/api/test")

    @responses.activate
    def test_timeout_error(self, client):
        """Test timeout error handling."""
        responses.add(
            responses.GET, "https://test.example.com/api/test", body=Timeout("Timeout")
        )

        with pytest.raises(FrappeConnectionError, match="Request timed out"):
            client.get("/api/test")


class TestRetryLogic:
    """Test retry logic."""

    @responses.activate
    def test_retry_on_500(self, client, api_responses):
        """Test retry on 500 error."""
        # First two attempts fail, third succeeds
        responses.add(
            responses.GET,
            "https://test.example.com/api/test",
            json=api_responses["error_500"],
            status=500,
        )
        responses.add(
            responses.GET,
            "https://test.example.com/api/test",
            json=api_responses["error_500"],
            status=500,
        )
        responses.add(
            responses.GET,
            "https://test.example.com/api/test",
            json=api_responses["success_response"],
            status=200,
        )

        result = client.get("/api/test")
        assert result == api_responses["success_response"]["message"]
        assert len(responses.calls) == 3

    @responses.activate
    def test_no_retry_on_404(self, client, api_responses):
        """Test no retry on 404 error."""
        responses.add(
            responses.GET,
            "https://test.example.com/api/test",
            json=api_responses["error_404"],
            status=404,
        )

        with pytest.raises(FrappeAPIError):
            client.get("/api/test")

        # Should only make one request (no retries)
        assert len(responses.calls) == 1

    @responses.activate
    def test_retry_on_connection_error(self, client, api_responses):
        """Test retry on connection error."""
        # First attempt fails, second succeeds
        responses.add(
            responses.GET,
            "https://test.example.com/api/test",
            body=ConnectionError("Connection refused"),
        )
        responses.add(
            responses.GET,
            "https://test.example.com/api/test",
            json=api_responses["success_response"],
            status=200,
        )

        result = client.get("/api/test")
        assert result == api_responses["success_response"]["message"]
        assert len(responses.calls) == 2


class TestURLBuilding:
    """Test URL building."""

    def test_url_concatenation(self, client):
        """Test URL path concatenation."""
        assert client._build_url("/api/test") == "https://test.example.com/api/test"
        assert client._build_url("api/test") == "https://test.example.com/api/test"

    def test_url_with_params(self, client):
        """Test URL building with query parameters."""
        url = client._build_url("/api/test", params={"limit": 10, "offset": 0})
        assert "limit=10" in url
        assert "offset=0" in url
