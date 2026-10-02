"""Search response parser for JetSmartFilters responses."""

from typing import Any
from bs4 import BeautifulSoup
from alecorretora_research.domain.listing import ListingCollection, ListingSummary
from alecorretora_research.parsers.feature_extractor import CardFeatureExtractor


PUBLIC_BASE_URL = "https://alecorretoramg.com.br/"


class SearchResponseParser:
    """Parses JetSmartFilters AJAX responses into ListingCollection."""

    def __init__(
        self,
        extractor: CardFeatureExtractor | None = None,
        public_base_url: str = PUBLIC_BASE_URL,
    ) -> None:
        """Initialize parser with an optional public website origin."""
        self._extractor = extractor or CardFeatureExtractor(public_base_url)

    def parse(
        self,
        raw_response: dict[str, Any] | str,
        current_page: int = 1,
    ) -> ListingCollection:
        """Parse JSON response or raw HTML into domain ListingCollection."""
        html_content, pagination = self._unwrap_payload(raw_response)
        soup = BeautifulSoup(html_content, "html.parser")
        cards = soup.find_all(class_="jet-listing-grid__item")

        listings: list[ListingSummary] = []
        for card in cards:
            summary = self._extractor.extract(card)
            listings.append(summary)

        total_found = pagination.get("found_posts", len(listings))
        max_pages = pagination.get("max_num_pages", 1 if listings else 0)

        return ListingCollection(
            listings=listings,
            total_found=int(total_found),
            max_pages=int(max_pages),
            current_page=current_page,
        )

    def _unwrap_payload(
        self, raw_response: dict[str, Any] | str
    ) -> tuple[str, dict[str, Any]]:
        """Extract HTML content string and pagination dictionary."""
        if isinstance(raw_response, dict):
            content = str(raw_response.get("content", ""))
            pagination = raw_response.get("pagination", {})
            if isinstance(pagination, dict):
                return content, pagination
            return content, {}
        return str(raw_response), {}
