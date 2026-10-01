"""Detailed property domain model and photo gallery collection."""

from dataclasses import dataclass
from typing import Iterator


class PhotoGallery:
    """First-class collection representing a property's photo gallery."""

    def __init__(self, photo_urls: list[str] | None = None) -> None:
        """Initialize photo collection with validated URLs."""
        self._photos = [url.strip() for url in (photo_urls or []) if url.strip()]

    def __iter__(self) -> Iterator[str]:
        """Iterate over photo URLs."""
        return iter(self._photos)

    def __len__(self) -> int:
        """Return total number of photos."""
        return len(self._photos)

    def __getitem__(self, index: int) -> str:
        """Retrieve photo by index."""
        return self._photos[index]

    def primary_photo(self) -> str | None:
        """Return the primary photo URL if available."""
        if not self._photos:
            return None
        return self._photos[0]


@dataclass(frozen=True)
class PropertyLocation:
    """Encapsulates geographical address attributes of a property."""

    neighborhood: str
    city: str
    state: str = "MG"


@dataclass(frozen=True)
class PropertySpecs:
    """Encapsulates physical specification attributes of a property."""

    bedrooms: int | None = None
    bathrooms: int | None = None
    parking_spaces: int | None = None
    area: str | None = None


@dataclass(frozen=True)
class PropertyDetail:
    """Full detail view for a specific property listing."""

    property_id: str
    url: str
    code: str
    title: str
    purpose: str
    price_formatted: str
    description: str
    location: PropertyLocation
    specs: PropertySpecs
    gallery: PhotoGallery
