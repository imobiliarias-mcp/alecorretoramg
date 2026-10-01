"""Geographical metadata domain entities and collections."""

from dataclasses import dataclass, field
from typing import Iterator


@dataclass(frozen=True)
class City:
    """Represents a city recognized by Alê Corretora MG."""

    city_id: str
    name: str
    slug: str


@dataclass(frozen=True)
class Neighborhood:
    """Represents a neighborhood recognized by Alê Corretora MG."""

    neighborhood_id: str
    name: str
    slug: str
    city_id: str | None = None


class CityCatalog:
    """First-class collection of cities."""

    def __init__(self, cities: list[City] | None = None) -> None:
        """Initialize collection of cities."""
        self._cities = list(cities or [])

    def __iter__(self) -> Iterator[City]:
        """Iterate through cities."""
        return iter(self._cities)

    def __len__(self) -> int:
        """Return total cities count."""
        return len(self._cities)

    def find_by_name(self, name: str) -> City | None:
        """Find city by case-insensitive name."""
        target = name.strip().lower()
        for item in self._cities:
            if item.name.lower() == target:
                return item
        return None

    def find_by_id(self, city_id: str) -> City | None:
        """Find city by numeric ID."""
        for item in self._cities:
            if item.city_id == city_id:
                return item
        return None


class NeighborhoodCatalog:
    """First-class collection of neighborhoods."""

    def __init__(self, neighborhoods: list[Neighborhood] | None = None) -> None:
        """Initialize collection of neighborhoods."""
        self._neighborhoods = list(neighborhoods or [])

    def __iter__(self) -> Iterator[Neighborhood]:
        """Iterate through neighborhoods."""
        return iter(self._neighborhoods)

    def __len__(self) -> int:
        """Return total neighborhoods count."""
        return len(self._neighborhoods)

    def find_by_name(self, name: str) -> Neighborhood | None:
        """Find neighborhood by case-insensitive name."""
        target = name.strip().lower()
        for item in self._neighborhoods:
            if item.name.lower() == target:
                return item
        return None

    def find_by_id(self, neighborhood_id: str) -> Neighborhood | None:
        """Find neighborhood by numeric ID."""
        for item in self._neighborhoods:
            if item.neighborhood_id == neighborhood_id:
                return item
        return None


class LocationCatalog:
    """Aggregate catalog wrapping city and neighborhood collections."""

    def __init__(
        self,
        cities: CityCatalog | None = None,
        neighborhoods: NeighborhoodCatalog | None = None,
    ) -> None:
        """Initialize composite location catalog."""
        self._cities = cities or CityCatalog()
        self._neighborhoods = neighborhoods or NeighborhoodCatalog()

    @property
    def cities(self) -> CityCatalog:
        """Access city catalog."""
        return self._cities

    @property
    def neighborhoods(self) -> NeighborhoodCatalog:
        """Access neighborhood catalog."""
        return self._neighborhoods
