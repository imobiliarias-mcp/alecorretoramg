"""Domain layer package exports for Alê Corretora MG research."""

from alecorretora_research.domain.criteria import (
    FilterCriteria,
    PaginationCriteria,
    SearchCriteria,
)
from alecorretora_research.domain.enums import PropertyType, TransactionType
from alecorretora_research.domain.listing import ListingCollection, ListingSummary
from alecorretora_research.domain.metadata import (
    City,
    CityCatalog,
    LocationCatalog,
    Neighborhood,
    NeighborhoodCatalog,
)
from alecorretora_research.domain.property import (
    PhotoGallery,
    PropertyDetail,
    PropertyLocation,
    PropertySpecs,
)
from alecorretora_research.domain.values import (
    PageNumber,
    PriceRange,
    PropertyCode,
    RoomCount,
)

__all__ = [
    "City",
    "CityCatalog",
    "FilterCriteria",
    "ListingCollection",
    "ListingSummary",
    "LocationCatalog",
    "Neighborhood",
    "NeighborhoodCatalog",
    "PageNumber",
    "PaginationCriteria",
    "PhotoGallery",
    "PriceRange",
    "PropertyCode",
    "PropertyDetail",
    "PropertyLocation",
    "PropertySpecs",
    "PropertyType",
    "RoomCount",
    "SearchCriteria",
    "TransactionType",
]
