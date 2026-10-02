"""Unit tests for search, detail, and metadata parsers."""

import pytest

from alecorretora_research.parsers.detail_parser import PropertyDetailParser
from alecorretora_research.parsers.feature_extractor import CardFeatureExtractor
from alecorretora_research.parsers.metadata_parser import MetadataParser
from alecorretora_research.parsers.search_parser import SearchResponseParser

SAMPLE_CARD_HTML = """
<div class="jet-listing-grid__item" data-post-id="11217">
  <style>background-image:url("https://alecorretoramg.com.br/sample.jpg");</style>
  <div class="jet-engine-listing-overlay-wrap" data-url="https://alecorretoramg.com.br/imoveis/loja-comercial-8-2/"></div>
  <h2 class="elementor-heading-title">Alugar</h2>
  <h2 class="elementor-heading-title">Cod. 0473</h2>
  <h2 class="elementor-heading-title">Loja Comercial</h2>
  <a class="jet-listing-dynamic-terms__link" href="https://alecorretoramg.com.br/bairro/garapa/">Garapa</a>
  <a class="jet-listing-dynamic-terms__link" href="https://alecorretoramg.com.br/cidade/timoteo/">Timóteo</a>
  <ul class="elementor-icon-list-items">
    <li class="elementor-icon-list-item"><span class="elementor-icon-list-text">1</span></li>
    <li class="elementor-icon-list-item"><span class="elementor-icon-list-text">1</span></li>
    <li class="elementor-icon-list-item"><span class="elementor-icon-list-text"></span></li>
    <li class="elementor-icon-list-item"><span class="elementor-icon-list-text">50m²</span></li>
  </ul>
  <div class="jet-listing-dynamic-field__content">R$ 700,00</div>
</div>
"""

SAMPLE_DETAIL_HTML = """
<html>
  <body>
    <h1>Loja Comercial/Quitinete</h1>
    <h2>Código do Imóvel: 0473</h2>
    <div class="jet-listing-dynamic-field">R$ 700,00</div>
    <div class="elementor-widget-text-editor">
      Loja Comercial localizada no bairro Garapa, em Timóteo/MG. Dividida em 3 partes.
    </div>
    <div data-widget_type="icon-list.default">
      <li class="elementor-icon-list-item">Quartos: 1</li>
      <li class="elementor-icon-list-item">Banheiros: 1</li>
      <li class="elementor-icon-list-item">Área: 50m²</li>
    </div>
    <div data-widget_type="image-carousel.default">
      <a href="https://alecorretoramg.com.br/uploads/photo1.jpg">Photo 1</a>
      <a href="https://alecorretoramg.com.br/uploads/photo2.png">Photo 2</a>
    </div>
  </body>
</html>
"""


def test_search_parser_with_stubbed_json() -> None:
    """Test search response parser with JSON structure."""
    payload = {
        "content": SAMPLE_CARD_HTML,
        "pagination": {"found_posts": 1, "max_num_pages": 1, "page": 1},
    }
    parser = SearchResponseParser()
    collection = parser.parse(payload, current_page=1)

    assert len(collection) == 1
    item = collection[0]
    assert item.property_id == "11217"
    assert item.code == "0473"
    assert item.price_formatted == "R$ 700,00"
    assert item.bedrooms == 1
    assert item.bathrooms == 1
    assert item.area == "50m²"
    assert item.thumbnail_url == "https://alecorretoramg.com.br/sample.jpg"


@pytest.mark.parametrize(
    ("card_url", "expected_url"),
    [
        (
            "https://alecorretoramg.com.br/imoveis/existing/",
            "https://alecorretoramg.com.br/imoveis/existing/",
        ),
        (
            "/imoveis/relative/",
            "https://alecorretoramg.com.br/imoveis/relative/",
        ),
        (
            "//alecorretoramg.com.br/imoveis/protocol-relative/",
            "https://alecorretoramg.com.br/imoveis/protocol-relative/",
        ),
        ("?id=608", "https://alecorretoramg.com.br/?id=608"),
    ],
)
def test_search_parser_resolves_card_urls(card_url: str, expected_url: str) -> None:
    """Resolve absolute, relative, protocol-relative, and identifier links."""
    card = SAMPLE_CARD_HTML.replace(
        "https://alecorretoramg.com.br/imoveis/loja-comercial-8-2/", card_url
    )
    collection = SearchResponseParser().parse({"content": card})

    assert collection[0].url == expected_url


def test_search_parser_uses_injected_public_base_url() -> None:
    """Resolve a relative card link against configured public, not API, origin."""
    card = SAMPLE_CARD_HTML.replace(
        "https://alecorretoramg.com.br/imoveis/loja-comercial-8-2/",
        "/imoveis/configured/",
    )
    parser = SearchResponseParser(public_base_url="https://public.example/")

    assert parser.parse({"content": card})[0].url == "https://public.example/imoveis/configured/"


@pytest.mark.parametrize("card_url", ["javascript:alert(1)", ""])
def test_search_parser_rejects_unrecoverable_card_url(card_url: str) -> None:
    """Reject invalid or absent links with listing context."""
    card = SAMPLE_CARD_HTML.replace(
        "https://alecorretoramg.com.br/imoveis/loja-comercial-8-2/", card_url
    )

    with pytest.raises(ValueError, match="11217"):
        SearchResponseParser().parse({"content": card})


@pytest.mark.parametrize(
    "card_url",
    [
        "https://bad host.example/imoveis/listing/",
        "https://user:password@alecorretoramg.com.br/imoveis/listing/",
        "https://alecorretoramg.com.br:invalid/imoveis/listing/",
        "https://[invalid]/imoveis/listing/",
        "https://alecorretoramg.com.br/wp-json/wp/v2/properties/11217",
        "https://alecorretoramg.com.br/wp-content/uploads/photo.jpg",
        "https://alecorretoramg.com.br/wp-admin/admin-ajax.php?action=jet_smart_filters",
    ],
)
def test_search_parser_rejects_invalid_public_listing_urls(card_url: str) -> None:
    """Reject malformed authorities and non-property endpoint URLs."""
    card = SAMPLE_CARD_HTML.replace(
        "https://alecorretoramg.com.br/imoveis/loja-comercial-8-2/", card_url
    )

    with pytest.raises(ValueError, match="11217"):
        SearchResponseParser().parse({"content": card})


@pytest.mark.parametrize(
    "public_base_url",
    [
        "https://bad host.example/",
        "https://user:password@public.example/",
        "https://public.example:invalid/",
        "https://[invalid]/",
    ],
)
def test_search_parser_rejects_malformed_public_base(public_base_url: str) -> None:
    """Reject malformed origin configuration before parsing listings."""
    with pytest.raises(ValueError, match="public base URL"):
        SearchResponseParser(public_base_url=public_base_url)


def test_property_detail_parser() -> None:
    """Test detail parser with sample HTML markup."""
    parser = PropertyDetailParser()
    detail = parser.parse(
        html_content=SAMPLE_DETAIL_HTML,
        property_id="11217",
        canonical_url="https://alecorretoramg.com.br/imoveis/loja-comercial-8-2/",
    )

    assert detail.code == "0473"
    assert detail.title == "Loja Comercial/Quitinete"
    assert detail.price_formatted == "R$ 700,00"
    assert detail.location.neighborhood == "Garapa"
    assert detail.location.city == "Timóteo"
    assert detail.specs.bedrooms == 1
    assert detail.specs.bathrooms == 1
    assert detail.specs.area == "Área: 50m²"
    assert len(detail.gallery) == 2
    assert detail.gallery[0] == "https://alecorretoramg.com.br/uploads/photo1.jpg"


def test_metadata_parser_api_json() -> None:
    """Test location parser with API JSON arrays."""
    cities = [{"id": 24, "name": "Timóteo", "slug": "timoteo"}]
    bairros = [{"id": 35, "name": "Funcionários", "slug": "funcionarios"}]

    parser = MetadataParser()
    catalog = parser.parse_api_json(cities, bairros)

    assert len(catalog.cities) == 1
    assert catalog.cities.find_by_name("timóteo") is not None
    assert len(catalog.neighborhoods) == 1
    assert catalog.neighborhoods.find_by_name("funcionários") is not None
