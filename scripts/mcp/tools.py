"""Model Context Protocol (MCP) tool adapters for Central Rental Research."""

from typing import Any
from alecorretora_research.client import AleCorretoraRentalClient


class AleCorretoraMcpAdapter:
    """Adapts domain rental provider for consumption by MCP servers and tool registries."""

    def __init__(self, client: Any = None) -> None:
        """Initialize adapter with an abstract rental client."""
        self._client = client or AleCorretoraRentalClient()

    @classmethod
    def create_default(cls) -> "AleCorretoraMcpAdapter":
        """Factory constructor instantiating the default Alê Corretora provider."""
        return cls(client=AleCorretoraRentalClient())

    def search_rentals(
        self,
        city: str = "",
        min_price: float = 0.0,
        max_price: float = 0.0,
        bedrooms: int = 0,
        property_type: str = "",
        page: int = 1,
    ) -> dict[str, Any]:
        """Execute a rental property search for an MCP tool call."""
        min_p = int(min_price) if min_price > 0 else None
        max_p = int(max_price) if max_price > 0 else None
        bed = bedrooms if bedrooms > 0 else None
        results = self._client.search_rentals(
            bedrooms=bed,
            min_price=min_p,
            max_price=max_p,
            page=page,
        )
        return self._format_collection(results)

    def _format_collection(self, collection: Any) -> dict[str, Any]:
        """Format collection into standard dictionary."""
        return {
            "provider": "alecorretoramg",
            "total_count": len(collection),
            "listings": [self._format_item(item) for item in collection],
        }

    def _format_item(self, item: Any) -> dict[str, Any]:
        """Format individual listing item."""
        return {
            "id": getattr(item, "property_id", ""),
            "code": getattr(item, "code", ""),
            "title": getattr(item, "title", ""),
            "price": getattr(item, "price_formatted", ""),
            "url": getattr(item, "url", ""),
            "neighborhood": getattr(getattr(item, "location", None), "neighborhood", ""),
            "city": getattr(getattr(item, "location", None), "city", ""),
        }

    def get_property_detail(self, property_code: str) -> dict[str, Any]:
        """Retrieve complete property detail for an MCP tool call."""
        detail = self._client.get_details(property_code)
        loc = detail.location
        specs = detail.specs
        return {
            "id": detail.property_id,
            "code": detail.code,
            "title": detail.title,
            "description": detail.description,
            "price": detail.price_formatted,
            "url": detail.url,
            "neighborhood": loc.neighborhood,
            "city": loc.city,
            "bedrooms": specs.bedrooms,
            "bathrooms": specs.bathrooms,
            "parking_spaces": specs.parking_spaces,
            "area": specs.area,
            "photos": list(detail.gallery),
        }

    def get_facets(self) -> dict[str, Any]:
        """Retrieve available search facets for an MCP tool call."""
        locations = self._client.get_locations()
        cities = [{"city_id": c.city_id, "name": c.name} for c in locations.cities]
        neighborhoods = [{"neighborhood_id": n.neighborhood_id, "name": n.name} for n in locations.neighborhoods]
        return {"cities": cities, "neighborhoods": neighborhoods}

    def get_provider_info(self) -> dict[str, Any]:
        """Retrieve metadata about this rental provider adapter."""
        return {
            "provider_name": "alecorretoramg",
            "coverage_region": "Timóteo e Vale do Aço",
            "supported_operations": ["search_rentals", "get_property_detail", "get_facets"],
        }
