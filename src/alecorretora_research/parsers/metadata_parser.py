"""Location metadata parser for REST API and HTML select dropdowns."""

from typing import Any
from bs4 import BeautifulSoup
from alecorretora_research.domain.metadata import (
    City,
    CityCatalog,
    LocationCatalog,
    Neighborhood,
    NeighborhoodCatalog,
)


class MetadataParser:
    """Parses taxonomy data into LocationCatalog collection."""

    def parse_api_json(
        self,
        cities_data: list[dict[str, Any]],
        neighborhoods_data: list[dict[str, Any]],
    ) -> LocationCatalog:
        """Parse REST API taxonomy JSON responses into LocationCatalog."""
        cities = self._parse_cities(cities_data)
        neighborhoods = self._parse_neighborhoods(neighborhoods_data)
        return LocationCatalog(
            cities=CityCatalog(cities),
            neighborhoods=NeighborhoodCatalog(neighborhoods),
        )

    def parse_html_page(self, html_content: str) -> LocationCatalog:
        """Parse city and neighborhood dropdown options from search page HTML."""
        soup = BeautifulSoup(html_content, "html.parser")
        cities = self._parse_select_options(soup, "cidade")
        neighborhoods = self._parse_select_options(soup, "bairro")
        return LocationCatalog(
            cities=CityCatalog(cities),
            neighborhoods=NeighborhoodCatalog(neighborhoods),
        )

    def _parse_cities(self, raw_items: list[dict[str, Any]]) -> list[City]:
        """Convert raw city dicts into City domain entities."""
        items: list[City] = []
        for d in raw_items:
            city_id = str(d.get("id", ""))
            name = str(d.get("name", ""))
            slug = str(d.get("slug", ""))
            if city_id and name:
                items.append(City(city_id=city_id, name=name, slug=slug))
        return items

    def _parse_neighborhoods(self, raw_items: list[dict[str, Any]]) -> list[Neighborhood]:
        """Convert raw neighborhood dicts into Neighborhood domain entities."""
        items: list[Neighborhood] = []
        for d in raw_items:
            n_id = str(d.get("id", ""))
            name = str(d.get("name", ""))
            slug = str(d.get("slug", ""))
            if n_id and name:
                items.append(Neighborhood(neighborhood_id=n_id, name=name, slug=slug))
        return items

    def _parse_select_options(self, soup: BeautifulSoup, query_var: str) -> list[Any]:
        """Extract options from JetSmartFilters select container."""
        container = soup.find(attrs={"data-query-var": query_var})
        if not container:
            return []
        select = container.find("select")
        if not select:
            return []
        return self._extract_options_from_select(select, query_var)

    def _extract_options_from_select(self, select: Any, query_var: str) -> list[Any]:
        """Convert select option tags into domain objects."""
        results: list[Any] = []
        for opt in select.find_all("option"):
            val = opt.get("value", "").strip()
            name = opt.get_text(strip=True)
            if not val or "Selecionar" in name:
                continue
            if query_var == "cidade":
                results.append(City(city_id=val, name=name, slug=""))
            if query_var == "bairro":
                results.append(Neighborhood(neighborhood_id=val, name=name, slug=""))
        return results
