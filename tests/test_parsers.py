"""Unit tests for search, detail, and metadata parsers."""

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
