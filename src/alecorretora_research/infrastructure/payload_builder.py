"""Payload builder and URL constructor for Alê Corretora MG portal."""

from typing import Any
import urllib.parse
from alecorretora_research.domain.criteria import SearchCriteria


class RequestPayloadBuilder:
    """Builds AJAX form payloads and URL paths for Alê Corretora MG."""

    BASE_URL = "https://alecorretoramg.com.br"
    AJAX_ENDPOINT = "https://alecorretoramg.com.br/wp-admin/admin-ajax.php"
    DEFAULT_LISTING_ID = "6919"
    DEFAULT_PAGE_SIZE = 10

    def __init__(self, base_url: str | None = None) -> None:
        """Initialize builder with optional custom base URL."""
        self._base = (base_url or self.BASE_URL).rstrip("/")

    @property
    def ajax_url(self) -> str:
        """Return AJAX endpoint URL."""
        return f"{self._base}/wp-admin/admin-ajax.php"

    def build_search_form_data(self, criteria: SearchCriteria) -> dict[str, str]:
        """Convert SearchCriteria into PHP-formatted flat dictionary for urlencode."""
        payload = self._build_raw_payload(criteria)
        return dict(self._flatten_php_data(payload))

    def build_detail_url(self, property_id_or_slug: str) -> str:
        """Build canonical property detail URL from ID or slug."""
        target = property_id_or_slug.strip().strip("/")
        if target.isdigit():
            return f"{self._base}/?p={target}"
        return f"{self._base}/imoveis/{target}/"

    def build_taxonomy_url(self, taxonomy: str, per_page: int = 100) -> str:
        """Build REST API URL for given taxonomy terms."""
        return f"{self._base}/wp-json/wp/v2/{taxonomy}?per_page={per_page}"

    def _build_raw_payload(self, criteria: SearchCriteria) -> dict[str, Any]:
        """Construct raw nested dictionary matching JetSmartFilters payload."""
        return {
            "action": "jet_smart_filters",
            "provider": "jet-engine/todos",
            "defaults": {
                "post_status": ["publish"],
                "post_type": "imoveis",
                "posts_per_page": str(self.DEFAULT_PAGE_SIZE),
                "paged": "1",
                "ignore_sticky_posts": "1",
            },
            "settings": {
                "lisitng_id": self.DEFAULT_LISTING_ID,
                "posts_num": self.DEFAULT_PAGE_SIZE,
            },
            "props": {
                "found_posts": self.DEFAULT_PAGE_SIZE,
                "max_num_pages": 1,
                "page": 1,
            },
            "query": criteria.to_query_dict(),
            "paged": criteria.page_number,
        }

    def _flatten_php_data(self, data: Any, prefix: str = "") -> list[tuple[str, str]]:
        """Recursively flatten nested dictionary and lists into PHP form tuples."""
        if isinstance(data, dict):
            return self._flatten_dict(data, prefix)
        if isinstance(data, (list, tuple)):
            return self._flatten_list(data, prefix)
        return [(prefix, str(data))]

    def _flatten_dict(self, data: dict[str, Any], prefix: str) -> list[tuple[str, str]]:
        """Flatten dictionary entries."""
        items: list[tuple[str, str]] = []
        for key, value in data.items():
            field_name = f"{prefix}[{key}]" if prefix else key
            items.extend(self._flatten_php_data(value, field_name))
        return items

    def _flatten_list(self, data: list[Any] | tuple[Any, ...], prefix: str) -> list[tuple[str, str]]:
        """Flatten list entries."""
        items: list[tuple[str, str]] = []
        for idx, value in enumerate(data):
            field_name = f"{prefix}[{idx}]" if prefix else str(idx)
            items.extend(self._flatten_php_data(value, field_name))
        return items
