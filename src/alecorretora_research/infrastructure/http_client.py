"""HTTP client abstractions, response representations, and exceptions."""

from dataclasses import dataclass
from typing import Any, Protocol
import httpx


class RentalResearchError(Exception):
    """Base exception for rental research operations."""


class PropertyNotFoundError(RentalResearchError):
    """Raised when a requested property cannot be found or returns 404."""


class SearchRequestError(RentalResearchError):
    """Raised when search request fails or returns invalid response."""


class InvalidCriteriaError(RentalResearchError):
    """Raised when provided search criteria is invalid or inconsistent."""


@dataclass(frozen=True)
class HttpResponse:
    """Standardized HTTP response abstraction."""

    status_code: int
    text: str
    final_url: str
    json_data: dict[str, Any] | None = None


class HttpClientProtocol(Protocol):
    """Protocol defining network transport contract."""

    def get(self, url: str, headers: dict[str, str] | None = None) -> HttpResponse:
        """Perform HTTP GET request."""
        ...

    def post(
        self,
        url: str,
        data: dict[str, Any] | str,
        headers: dict[str, str] | None = None,
    ) -> HttpResponse:
        """Perform HTTP POST request."""
        ...


class HttpxHttpClient:
    """HTTP client implementation using HTTPX."""

    DEFAULT_HEADERS = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
    }

    def __init__(self, timeout_seconds: float = 20.0) -> None:
        """Initialize HTTPX client with standard desktop headers and timeout."""
        self._client = httpx.Client(
            timeout=timeout_seconds,
            follow_redirects=True,
            headers=self.DEFAULT_HEADERS,
        )

    def get(self, url: str, headers: dict[str, str] | None = None) -> HttpResponse:
        """Execute GET request and convert response."""
        try:
            resp = self._client.get(url, headers=headers)
            json_payload = self._try_extract_json(resp)
            return HttpResponse(
                status_code=resp.status_code,
                text=resp.text,
                final_url=str(resp.url),
                json_data=json_payload,
            )
        except httpx.HTTPError as exc:
            raise SearchRequestError(f"HTTP GET failed for {url}: {exc}") from exc

    def post(
        self,
        url: str,
        data: dict[str, Any] | str,
        headers: dict[str, str] | None = None,
    ) -> HttpResponse:
        """Execute POST request with form-encoded or raw data."""
        try:
            resp = self._client.post(url, data=data, headers=headers)
            json_payload = self._try_extract_json(resp)
            return HttpResponse(
                status_code=resp.status_code,
                text=resp.text,
                final_url=str(resp.url),
                json_data=json_payload,
            )
        except httpx.HTTPError as exc:
            raise SearchRequestError(f"HTTP POST failed for {url}: {exc}") from exc

    def _try_extract_json(self, resp: httpx.Response) -> Any | None:
        """Safely attempt to parse JSON payload without throwing."""
        try:
            return resp.json()
        except Exception:
            return None
