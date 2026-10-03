"""Unit tests for AleCorretoraMcpAdapter."""

from scripts.mcp.tools import AleCorretoraMcpAdapter
from alecorretora_research.client import AleCorretoraRentalClient


class DummyClient:
    """Dummy client for testing Ale Corretora adapter without network."""

    def search_rentals(self, **kwargs):
        class DummyCollection(list):
            pass
        return DummyCollection()

    def get_details(self, ref):
        class DummyDetail:
            property_id = "123"
            code = "AP001"
            title = "Apartamento Centro"
            purpose = "aluguel"
            price_formatted = "R$ 1.500"
            description = "Lindo apartamento"
            url = "https://alecorretoramg.com.br/imovel/ap001"
            gallery = ["https://alecorretoramg.com.br/img1.jpg"]
            class location:
                neighborhood = "Centro"
                city = "Timóteo"
                state = "MG"
            class specs:
                bedrooms = 2
                bathrooms = 1
                parking_spaces = 1
                area = 70
        return DummyDetail()

    def get_locations(self):
        class DummyLocations:
            cities = []
            neighborhoods = []
        return DummyLocations()


def test_mcp_adapter_provider_info():
    """Test MCP provider metadata."""
    adapter = AleCorretoraMcpAdapter(client=DummyClient())
    info = adapter.get_provider_info()
    assert info["provider_name"] == "alecorretoramg"
    assert "search_rentals" in info["supported_operations"]


def test_mcp_adapter_search_rentals():
    """Test MCP search tool execution."""
    adapter = AleCorretoraMcpAdapter(client=DummyClient())
    result = adapter.search_rentals(city="Timóteo", bedrooms=2, max_price=1500.0)
    assert isinstance(result, dict)
    assert result["provider"] == "alecorretoramg"
    assert "listings" in result


def test_mcp_adapter_property_detail():
    """Test MCP detail tool execution."""
    adapter = AleCorretoraMcpAdapter(client=DummyClient())
    detail = adapter.get_property_detail("AP001")
    assert isinstance(detail, dict)
    assert detail["title"] == "Apartamento Centro"
