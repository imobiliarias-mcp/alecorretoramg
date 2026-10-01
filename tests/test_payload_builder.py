"""Unit tests for RequestPayloadBuilder."""

from alecorretora_research.domain.criteria import SearchCriteria
from alecorretora_research.domain.enums import PropertyType
from alecorretora_research.infrastructure.payload_builder import RequestPayloadBuilder


def test_payload_builder_ajax_endpoint() -> None:
    """Test AJAX URL construction."""
    builder = RequestPayloadBuilder()
    assert builder.ajax_url == "https://alecorretoramg.com.br/wp-admin/admin-ajax.php"


def test_payload_builder_detail_url() -> None:
    """Test detail URL generation for numeric IDs and slugs."""
    builder = RequestPayloadBuilder()
    assert builder.build_detail_url("11217") == "https://alecorretoramg.com.br/?p=11217"
    assert (
        builder.build_detail_url("loja-comercial-8-2")
        == "https://alecorretoramg.com.br/imoveis/loja-comercial-8-2/"
    )


def test_payload_builder_taxonomy_url() -> None:
    """Test REST API taxonomy URL."""
    builder = RequestPayloadBuilder()
    url = builder.build_taxonomy_url("cidade", per_page=50)
    assert url == "https://alecorretoramg.com.br/wp-json/wp/v2/cidade?per_page=50"


def test_payload_builder_search_form_data() -> None:
    """Test PHP form data flattening."""
    criteria = SearchCriteria.create_rental(
        city_id="24",
        property_type=PropertyType.APARTAMENTO,
        bedrooms=2,
        page=1,
    )
    builder = RequestPayloadBuilder()
    form_data = builder.build_search_form_data(criteria)

    assert form_data["action"] == "jet_smart_filters"
    assert form_data["provider"] == "jet-engine/todos"
    assert form_data["query[_tax_query_finalidade]"] == "21"
    assert form_data["query[_tax_query_tipo-de-imovel]"] == "8"
    assert form_data["query[_tax_query_cidade]"] == "24"
    assert form_data["query[_meta_query_quartos]"] == "2"
    assert form_data["paged"] == "1"
    assert form_data["defaults[post_type]"] == "imoveis"
