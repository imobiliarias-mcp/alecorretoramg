"""Listing summary and first-class collection domain models."""

from dataclasses import asdict, dataclass
from typing import Any, Iterator


@dataclass(frozen=True)
class ListingSummary:
    """Summary representation of a property in search result cards."""

    property_id: str
    url: str
    code: str
    title: str
    purpose: str
    property_type: str
    neighborhood: str
    city: str
    price_formatted: str
    bedrooms: int | None
    bathrooms: int | None
    parking_spaces: int | None
    area: str | None
    thumbnail_url: str | None

    def to_dictionary(self) -> dict[str, Any]:
        """Return every native listing field in a serializable dictionary."""
        return asdict(self)


class ListingCollection:
    """First-class collection representing search result listings and pagination."""

    def __init__(
        self,
        listings: list[ListingSummary] | None = None,
        total_found: int = 0,
        max_pages: int = 0,
        current_page: int = 1,
    ) -> None:
        """Initialize collection of listing summaries with pagination state."""
        self._listings = list(listings or [])
        self._total_found = total_found
        self._max_pages = max_pages
        self._current_page = current_page

    def __iter__(self) -> Iterator[ListingSummary]:
        """Iterate over listings."""
        return iter(self._listings)

    def __len__(self) -> int:
        """Return number of listings on the current page."""
        return len(self._listings)

    def __getitem__(self, index: int) -> ListingSummary:
        """Access listing by index."""
        return self._listings[index]

    @property
    def total_found(self) -> int:
        """Total matching listings across all pages."""
        return self._total_found

    @property
    def max_pages(self) -> int:
        """Total number of available pages."""
        return self._max_pages

    @property
    def current_page(self) -> int:
        """Current page number."""
        return self._current_page

    def has_next_page(self) -> bool:
        """Determine if additional pages exist."""
        return self._current_page < self._max_pages

    def is_empty(self) -> bool:
        """Check if collection contains no listings."""
        return len(self._listings) == 0

    def to_dictionary(self) -> dict[str, Any]:
        """Serialize listings without losing search counts or page state."""
        return {
            "listings": [item.to_dictionary() for item in self._listings],
            "returned_count": len(self._listings),
            "total_found": self._total_found,
            "max_pages": self._max_pages,
            "current_page": self._current_page,
        }
