"""Unit tests for AleCorretoraRentalClient with test doubles."""

from typing import Any
import pytest
from alecorretora_research.client import AleCorretoraRentalClient
from alecorretora_research.collaborators import RentalNetworkGateway
from alecorretora_research.domain.criteria import SearchCriteria
from alecorretora_research.infrastructure.http_client import (
    HttpClientProtocol,
    HttpResponse,
    PropertyNotFoundError,
)

SAMPLE_CARD_HTML = """
<div class="jet-listing-grid__item" data-post-id="11217">
  <div class="jet-engine-listing-overlay-wrap" data-url="https://alecorretoramg.com.br/imoveis/loja-comercial-8-2/"></div>
  <h2 class="elementor-heading-title">Alugar</h2>
  <h2 class="elementor-heading-title">Cod. 0473</h2>
  <h2 class="elementor-heading-title">Loja Comercial</h2>
  <div class="jet-listing-dynamic-field__content">R$ 700,00</div>
</div>
"""

SAMPLE_DETAIL_HTML = """
<html><body>
  <h1>Loja Comercial/Quitinete</h1>
  <h2>Código do Imóvel: 0473</h2>
  <div class="jet-listing-dynamic-field">R$ 700,00</div>
</body></html>
"""


class StubHttpClient:
    """Stub network client for deterministic unit testing."""

    def __init__(self, not_found: bool = False) -> None:
        """Initialize stub behavior."""
        self._not_found = not_found

    def get(self, url: str, headers: dict[str, str] | None = None) -> HttpResponse:
        """Return stub detail or taxonomy response."""
        if self._not_found:
            return HttpResponse(status_code=404, text="Not Found", final_url=url)
        return HttpResponse(status_code=200, text=SAMPLE_DETAIL_HTML, final_url=url)

    def post(
        self,
        url: str,
        data: dict[str, Any] | str,
        headers: dict[str, str] | None = None,
    ) -> HttpResponse:
        """Return stub search response."""
        payload = {
            "content": SAMPLE_CARD_HTML,
            "pagination": {"found_posts": 1, "max_num_pages": 1, "page": 1},
        }
        return HttpResponse(
            status_code=200,
            text=SAMPLE_CARD_HTML,
            final_url=url,
            json_data=payload,
        )


def test_client_search_with_stub() -> None:
    """Test search workflow through client facade."""
    gateway = RentalNetworkGateway(http_client=StubHttpClient())
    client = AleCorretoraRentalClient(gateway=gateway)

    results = client.search_rentals(city_id="24", bedrooms=1)
    assert len(results) == 1
    assert results[0].code == "0473"
    assert results[0].price_formatted == "R$ 700,00"


def test_client_get_details_with_stub() -> None:
    """Test detail retrieval workflow through client facade."""
    gateway = RentalNetworkGateway(http_client=StubHttpClient())
    client = AleCorretoraRentalClient(gateway=gateway)

    detail = client.get_details("11217")
    assert detail.code == "0473"
    assert detail.title == "Loja Comercial/Quitinete"


def test_client_not_found_raises_exception() -> None:
    """Test 404 response raises PropertyNotFoundError."""
    gateway = RentalNetworkGateway(http_client=StubHttpClient(not_found=True))
    client = AleCorretoraRentalClient(gateway=gateway)

    with pytest.raises(PropertyNotFoundError):
        client.get_details("999999")
