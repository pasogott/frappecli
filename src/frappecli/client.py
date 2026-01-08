"""Frappe API client."""

import json
from typing import Any
from urllib.parse import urlencode, urljoin

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


class FrappeAPIError(Exception):
    """Frappe API error exception."""

    pass


class FrappeConnectionError(Exception):
    """Frappe connection error exception."""

    pass


class FrappeClient:
    """Frappe API client.

    Handles authentication and HTTP requests to Frappe REST API.
    Supports retry logic for transient failures.
    """

    def __init__(self, base_url: str, api_key: str, api_secret: str, timeout: int = 30) -> None:
        """Initialize Frappe API client.

        Args:
            base_url: Base URL of Frappe site (e.g., https://erp.example.com)
            api_key: API key for authentication
            api_secret: API secret for authentication
            timeout: Request timeout in seconds (default: 30)
        """
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

        # Create session with authentication
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Authorization": f"token {api_key}:{api_secret}",
                "Content-Type": "application/json",
            }
        )

        # Configure retry strategy
        self._configure_retries()

    def _configure_retries(self) -> None:
        """Configure retry strategy for transient failures."""
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[500, 502, 503, 504],
            allowed_methods=["GET", "POST", "PUT", "DELETE"],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

    def _build_url(self, path: str, params: dict[str, Any] | None = None) -> str:
        """Build full URL from path and parameters.

        Frappe API expects certain parameters (like filters) as JSON strings.

        Args:
            path: API path (with or without leading slash)
            params: Query parameters (optional)

        Returns:
            Full URL with parameters
        """
        # Ensure path starts with /
        if not path.startswith("/"):
            path = f"/{path}"

        url = urljoin(self.base_url, path)

        if params:
            # Convert dict/list params to JSON strings for Frappe API
            encoded_params = {}
            for key, value in params.items():
                if isinstance(value, dict | list):
                    # Serialize as JSON string
                    encoded_params[key] = json.dumps(value)
                else:
                    encoded_params[key] = value

            query_string = urlencode(encoded_params)
            url = f"{url}?{query_string}"

        return url

    def _make_request(
        self,
        method: str,
        path: str,
        data: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
    ) -> requests.Response:
        """Make HTTP request to Frappe API.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            path: API path
            data: Request body data (optional)
            params: Query parameters (optional)

        Returns:
            Response object

        Raises:
            FrappeConnectionError: If connection fails
            FrappeAPIError: If API returns error
        """
        url = self._build_url(path, params)

        try:
            response = self.session.request(method=method, url=url, json=data, timeout=self.timeout)
        except requests.exceptions.ConnectionError as e:
            msg = f"Failed to connect to {self.base_url}: {e}"
            raise FrappeConnectionError(msg) from e
        except requests.exceptions.Timeout as e:
            msg = f"Request timed out after {self.timeout} seconds: {e}"
            raise FrappeConnectionError(msg) from e
        except requests.exceptions.RequestException as e:
            msg = f"Request failed: {e}"
            raise FrappeConnectionError(msg) from e

        # Handle HTTP errors
        if not response.ok:
            self._handle_error_response(response)

        return response

    def _handle_error_response(self, response: requests.Response) -> None:
        """Handle error response from API.

        Args:
            response: Response object with error

        Raises:
            FrappeAPIError: Always raises with error details
        """
        status_code = response.status_code
        try:
            error_data = response.json()
            error_message = error_data.get("message", response.text)
        except Exception:
            error_message = response.text

        msg = f"API request failed with status {status_code}: {error_message}"
        raise FrappeAPIError(msg)

    def _parse_response(self, response: requests.Response) -> Any:
        """Parse response and extract data.

        Frappe API wraps responses in different ways:
        - {"message": ...} for RPC methods
        - {"data": [...]} for resource lists
        - Direct data for some endpoints

        Args:
            response: Response object

        Returns:
            Parsed response data (unwrapped)
        """
        try:
            data = response.json()
        except Exception:
            return response.text

        # Not a dict - return as-is
        if not isinstance(data, dict):
            return data

        # Priority 1: 'message' field (RPC methods, version info, etc.)
        if "message" in data:
            return data["message"]

        # Priority 2: 'data' field (resource lists)
        if "data" in data:
            return data["data"]

        # No wrapper - return as-is
        return data

    def get(self, path: str, params: dict[str, Any] | None = None) -> Any:
        """Make GET request.

        Args:
            path: API path
            params: Query parameters (optional)

        Returns:
            Response data
        """
        response = self._make_request("GET", path, params=params)
        return self._parse_response(response)

    def post(self, path: str, data: dict[str, Any] | None = None) -> Any:
        """Make POST request.

        Args:
            path: API path
            data: Request body data

        Returns:
            Response data
        """
        response = self._make_request("POST", path, data=data)
        return self._parse_response(response)

    def put(self, path: str, data: dict[str, Any] | None = None) -> Any:
        """Make PUT request.

        Args:
            path: API path
            data: Request body data

        Returns:
            Response data
        """
        response = self._make_request("PUT", path, data=data)
        return self._parse_response(response)

    def delete(self, path: str) -> Any:
        """Make DELETE request.

        Args:
            path: API path

        Returns:
            Response data
        """
        response = self._make_request("DELETE", path)
        return self._parse_response(response)
