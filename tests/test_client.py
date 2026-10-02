"""Unit tests for AleCorretoraRentalClient with test doubles."""

from typing import Any
import pytest
from alecorretora_research.client import AleCorretoraRentalClient
from alecorretora_research.collaborators import (
    ListingParserBundle,
    RentalNetworkGateway,
    RentalParserSuite,
)
from alecorretora_research.parsers.search_parser import SearchResponseParser
from alecorretora_research.domain.criteria import SearchCriteria
from alecorretora_research.domain.listing import ListingCollection, ListingSummary
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

    def __init__(
        self,
        not_found: bool = False,
        search_card_html: str = SAMPLE_CARD_HTML,
    ) -> None:
        """Initialize stub behavior."""
        self._not_found = not_found
        self._search_card_html = search_card_html
        self.search_calls = 0
        self.detail_calls = 0

    def get(self, url: str, headers: dict[str, str] | None = None) -> HttpResponse:
        """Return stub detail or taxonomy response."""
        self.detail_calls += 1
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
        self.search_calls += 1
        payload = {
            "content": self._search_card_html,
            "pagination": {"found_posts": 1, "max_num_pages": 1, "page": 1},
        }
        return HttpResponse(
            status_code=200,
            text=self._search_card_html,
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


def test_client_resolves_card_url_without_detail_lookup() -> None:
    """Use configured public origin through the real client parser pipeline."""
    relative_card = SAMPLE_CARD_HTML.replace(
        "https://alecorretoramg.com.br/imoveis/loja-comercial-8-2/",
        "/imoveis/from-card/",
    )
    transport = StubHttpClient(search_card_html=relative_card)
    parser = SearchResponseParser(public_base_url="https://public.example/")
    parsers = RentalParserSuite(
        listing_bundle=ListingParserBundle(search_parser=parser)
    )
    client = AleCorretoraRentalClient(
        gateway=RentalNetworkGateway(http_client=transport), parsers=parsers
    )

    results = client.search_rentals()

    assert results[0].url == "https://public.example/imoveis/from-card/"
    assert transport.search_calls == 1
    assert transport.detail_calls == 0


def test_existing_research_runner_prints_links(capsys) -> None:
    """Print each result URL from every existing search section."""
    from scripts.verify_research import (
        run_bedroom_filtered_search,
        run_code_search,
        run_price_range_search,
        run_target_rental_search,
    )

    listing = ListingSummary(
        property_id="11217",
        url="https://alecorretoramg.com.br/imoveis/loja/",
        code="0473",
        title="Loja",
        purpose="Alugar",
        property_type="Loja Comercial",
        neighborhood="Garapa",
        city="Timóteo",
        price_formatted="R$ 700,00",
        bedrooms=1,
        bathrooms=1,
        parking_spaces=None,
        area="50m²",
        thumbnail_url=None,
    )
    results = ListingCollection([listing], total_found=1)

    class StubClient:
        def search_rentals(self, **kwargs) -> ListingCollection:
            return results

    client = StubClient()
    run_target_rental_search(client)
    run_bedroom_filtered_search(client)
    run_price_range_search(client)
    run_code_search(client)
    output = capsys.readouterr().out

    assert output.count("Link: https://alecorretoramg.com.br/imoveis/loja/") == 4


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
