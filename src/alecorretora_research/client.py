"""Central rental research MCP interface and client."""

from typing import Any
from alecorretora_research.collaborators import RentalNetworkGateway, RentalParserSuite
from alecorretora_research.domain.criteria import SearchCriteria
from alecorretora_research.domain.enums import PropertyType
from alecorretora_research.domain.listing import ListingCollection
from alecorretora_research.domain.metadata import LocationCatalog
from alecorretora_research.domain.property import PropertyDetail


class AleCorretoraRentalClient:
    """Central rental research client serving as the project's MCP interface."""

    def __init__(
        self,
        gateway: RentalNetworkGateway | None = None,
        parsers: RentalParserSuite | None = None,
    ) -> None:
        """Initialize client with gateway and parser suite collaborators."""
        self._gateway = gateway or RentalNetworkGateway()
        self._parsers = parsers or RentalParserSuite()

    def search(self, criteria: SearchCriteria) -> ListingCollection:
        """Execute search query and return parsed collection of listings."""
        resp = self._gateway.fetch_search(criteria)
        parser = self._parsers.search_parser
        payload = resp.json_data if resp.json_data else resp.text
        return parser.parse(payload, current_page=criteria.page_number)

    def search_rentals(
        self,
        city_id: str | None = None,
        neighborhood_id: str | None = None,
        property_type: PropertyType = PropertyType.TODOS,
        bedrooms: int | None = None,
        bathrooms: int | None = None,
        min_price: int | None = None,
        max_price: int | None = None,
        code: str | None = None,
        page: int = 1,
    ) -> ListingCollection:
        """Convenience method for executing rental searches with standard filters."""
        criteria = SearchCriteria.create_rental(
            city_id=city_id,
            neighborhood_id=neighborhood_id,
            property_type=property_type,
            bedrooms=bedrooms,
            bathrooms=bathrooms,
            min_price=min_price,
            max_price=max_price,
            code=code,
            page=page,
        )
        return self.search(criteria)

    def get_details(self, property_id_or_slug: str) -> PropertyDetail:
        """Retrieve full details for a specific property by ID or URL slug."""
        resp = self._gateway.fetch_detail(property_id_or_slug)
        parser = self._parsers.detail_parser
        return parser.parse(
            html_content=resp.text,
            property_id=property_id_or_slug,
            canonical_url=resp.final_url,
        )

    def get_locations(self) -> LocationCatalog:
        """Retrieve catalog of cities and neighborhoods recognized by the portal."""
        cities_resp = self._gateway.fetch_taxonomy("cidade")
        bairros_resp = self._gateway.fetch_taxonomy("bairro")
        cities_data = cities_resp.json_data if isinstance(cities_resp.json_data, list) else []
        bairros_data = bairros_resp.json_data if isinstance(bairros_resp.json_data, list) else []
        parser = self._parsers.metadata_parser
        return parser.parse_api_json(cities_data, bairros_data)
