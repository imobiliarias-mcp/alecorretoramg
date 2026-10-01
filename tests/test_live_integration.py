"""Live integration tests against live portal alecorretoramg.com.br."""

import pytest
from alecorretora_research.client import AleCorretoraRentalClient
from alecorretora_research.domain.enums import PropertyType


@pytest.fixture
def live_client() -> AleCorretoraRentalClient:
    """Fixture providing initialized live client."""
    return AleCorretoraRentalClient()


def test_live_rental_search(live_client: AleCorretoraRentalClient) -> None:
    """Test live rental listing search flow."""
    results = live_client.search_rentals()
    assert results.total_found >= 4
    assert len(results) >= 4

    codes = [item.code for item in results]
    assert "0473" in codes
    assert "0462" in codes
    assert "0461" in codes
    assert "0363" in codes


def test_live_rental_filtered_by_bedrooms(live_client: AleCorretoraRentalClient) -> None:
    """Test filtering rentals by bedroom count."""
    results = live_client.search_rentals(bedrooms=2)
    assert len(results) >= 1
    codes = [item.code for item in results]
    assert "0462" in codes


def test_live_rental_filtered_by_price_range(live_client: AleCorretoraRentalClient) -> None:
    """Test filtering rentals by price range."""
    results = live_client.search_rentals(min_price=700, max_price=1500)
    assert results.total_found == 2
    codes = [item.code for item in results]
    assert "0473" in codes
    assert "0461" in codes


def test_live_rental_filtered_by_code(live_client: AleCorretoraRentalClient) -> None:
    """Test searching property by reference code."""
    results = live_client.search_rentals(code="0473")
    assert len(results) == 1
    assert results[0].code == "0473"
    assert "700" in results[0].price_formatted


def test_live_property_detail_retrieval(live_client: AleCorretoraRentalClient) -> None:
    """Test retrieving full property details for rental 11217."""
    detail = live_client.get_details("11217")
    assert detail.code == "0473"
    assert "Loja Comercial" in detail.title
    assert "700" in detail.price_formatted
    assert detail.specs.bedrooms == 1
    assert len(detail.gallery) > 0


def test_live_locations_retrieval(live_client: AleCorretoraRentalClient) -> None:
    """Test retrieving live cities and neighborhoods taxonomies."""
    catalog = live_client.get_locations()
    assert len(catalog.cities) >= 10
    timoteo = catalog.cities.find_by_name("timóteo")
    assert timoteo is not None
    assert timoteo.city_id == "24"
    assert len(catalog.neighborhoods) >= 50
