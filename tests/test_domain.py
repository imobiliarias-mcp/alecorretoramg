"""Unit tests for domain layer value objects, entities, and collections."""

import pytest
from alecorretora_research.domain.criteria import SearchCriteria
from alecorretora_research.domain.enums import PropertyType, TransactionType
from alecorretora_research.domain.listing import ListingCollection, ListingSummary
from alecorretora_research.domain.metadata import City, CityCatalog, LocationCatalog, Neighborhood, NeighborhoodCatalog
from alecorretora_research.domain.property import PhotoGallery
from alecorretora_research.domain.values import (
    PageNumber,
    PriceRange,
    PropertyCode,
    RoomCount,
)


def test_price_range_validations() -> None:
    """Test price range boundary checks and query serialization."""
    valid_range = PriceRange(min_price=700, max_price=1500)
    assert valid_range.to_query_value() == "700_1500"

    min_only = PriceRange(min_price=500)
    assert min_only.to_query_value() == "500_5000000"

    max_only = PriceRange(max_price=3000)
    assert max_only.to_query_value() == "0_3000"

    empty = PriceRange()
    assert empty.to_query_value() is None

    with pytest.raises(ValueError):
        PriceRange(min_price=-10)

    with pytest.raises(ValueError):
        PriceRange(min_price=2000, max_price=1000)


def test_room_count_validations() -> None:
    """Test room count query formatting and guard clauses."""
    assert RoomCount(1).to_query_value() == "1"
    assert RoomCount(2).to_query_value() == "2"
    assert RoomCount(4).to_query_value() == "4"
    assert RoomCount(6).to_query_value() == "4"

    with pytest.raises(ValueError):
        RoomCount(-1)


def test_page_number_validations() -> None:
    """Test pagination number constraints."""
    assert PageNumber(1).value == 1
    assert PageNumber(5).value == 5

    with pytest.raises(ValueError):
        PageNumber(0)


def test_property_code_validations() -> None:
    """Test property code cleaning and validation."""
    code = PropertyCode("  0473  ")
    assert code.value == "0473"

    with pytest.raises(ValueError):
        PropertyCode("   ")


def test_search_criteria_rental_factory() -> None:
    """Test rental search criteria query parameter generation."""
    criteria = SearchCriteria.create_rental(
        city_id="24",
        neighborhood_id="35",
        property_type=PropertyType.APARTAMENTO,
        bedrooms=2,
        bathrooms=1,
        min_price=700,
        max_price=1600,
        code="0462",
        page=2,
    )
    query = criteria.to_query_dict()

    assert query["_tax_query_finalidade"] == TransactionType.ALUGAR.value
    assert query["_tax_query_tipo-de-imovel"] == PropertyType.APARTAMENTO.value
    assert query["_tax_query_cidade"] == "24"
    assert query["_tax_query_bairro"] == "35"
    assert query["_meta_query_quartos"] == "2"
    assert query["_meta_query_banheiros"] == "1"
    assert query["_meta_query_preco|range"] == "700_1600"
    assert query["_meta_query_codigo-do-imovel"] == "0462"
    assert criteria.page_number == 2


def test_listing_collection_behavior() -> None:
    """Test listing collection first-class collection protocol."""
    dummy_item = ListingSummary(
        property_id="11217",
        url="https://alecorretoramg.com.br/imoveis/loja-8/",
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
        thumbnail_url="https://alecorretoramg.com.br/thumb.jpg",
    )
    collection = ListingCollection(
        listings=[dummy_item],
        total_found=4,
        max_pages=2,
        current_page=1,
    )

    assert len(collection) == 1
    assert collection[0].code == "0473"
    assert collection.total_found == 4
    assert collection.max_pages == 2
    assert collection.has_next_page() is True
    assert collection.is_empty() is False


def test_listing_summary_and_collection_serialize_public_fields() -> None:
    """Serialize listing fields and preserve pagination metadata."""
    item = ListingSummary(
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
        thumbnail_url="https://alecorretoramg.com.br/thumb.jpg",
    )
    collection = ListingCollection(
        listings=[item, item], total_found=4, max_pages=2, current_page=1
    )

    serialized = collection.to_dictionary()

    assert len(serialized["listings"]) == 2
    assert serialized["listings"][0]["url"] == item.url
    assert serialized["listings"][0]["property_id"] == "11217"
    assert serialized["listings"][0]["price_formatted"] == "R$ 700,00"
    assert serialized["returned_count"] == 2
    assert serialized["total_found"] == 4
    assert serialized["max_pages"] == 2
    assert serialized["current_page"] == 1


def test_empty_listing_collection_serializes_zero_count() -> None:
    """Serialize an empty collection without changing its current-page count."""
    serialized = ListingCollection().to_dictionary()

    assert serialized["listings"] == []
    assert serialized["returned_count"] == 0
    assert serialized["total_found"] == 0


def test_photo_gallery_behavior() -> None:
    """Test photo gallery collection behavior."""
    gallery = PhotoGallery([" https://img1.jpg ", "https://img2.jpg", ""])
    assert len(gallery) == 2
    assert gallery.primary_photo() == "https://img1.jpg"
    assert gallery[1] == "https://img2.jpg"

    empty_gallery = PhotoGallery([])
    assert empty_gallery.primary_photo() is None


def test_location_catalog_lookups() -> None:
    """Test city and neighborhood catalog lookups."""
    cities = CityCatalog([City("24", "Timóteo", "timoteo")])
    bairros = NeighborhoodCatalog([Neighborhood("35", "Funcionários", "funcionarios")])
    catalog = LocationCatalog(cities=cities, neighborhoods=bairros)

    assert catalog.cities.find_by_name("timóteo") is not None
    assert catalog.cities.find_by_id("24") is not None
    assert catalog.cities.find_by_name("NonExistent") is None

    assert catalog.neighborhoods.find_by_name("funcionários") is not None
    assert catalog.neighborhoods.find_by_id("35") is not None
