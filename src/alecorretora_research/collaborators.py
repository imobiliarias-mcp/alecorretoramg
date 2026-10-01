"""Gateway and parser suite collaborators for rental research client."""

from alecorretora_research.domain.criteria import SearchCriteria
from alecorretora_research.infrastructure.http_client import (
    HttpClientProtocol,
    HttpResponse,
    HttpxHttpClient,
    PropertyNotFoundError,
)
from alecorretora_research.infrastructure.payload_builder import RequestPayloadBuilder
from alecorretora_research.parsers.detail_parser import PropertyDetailParser
from alecorretora_research.parsers.metadata_parser import MetadataParser
from alecorretora_research.parsers.search_parser import SearchResponseParser


class RentalNetworkGateway:
    """Dispatches HTTP requests for rental searches, details, and taxonomies."""

    def __init__(
        self,
        http_client: HttpClientProtocol | None = None,
        payload_builder: RequestPayloadBuilder | None = None,
    ) -> None:
        """Initialize gateway with transport client and payload builder."""
        self._http = http_client or HttpxHttpClient()
        self._builder = payload_builder or RequestPayloadBuilder()

    def fetch_search(self, criteria: SearchCriteria) -> HttpResponse:
        """Execute search POST request to JetSmartFilters AJAX endpoint."""
        url = self._builder.ajax_url
        data = self._builder.build_search_form_data(criteria)
        headers = {
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "X-Requested-With": "XMLHttpRequest",
        }
        return self._http.post(url, data=data, headers=headers)

    def fetch_detail(self, property_id_or_slug: str) -> HttpResponse:
        """Fetch detail page for a given property ID or slug."""
        url = self._builder.build_detail_url(property_id_or_slug)
        resp = self._http.get(url)
        self._validate_detail_response(resp, property_id_or_slug)
        return resp

    def fetch_taxonomy(self, taxonomy: str) -> HttpResponse:
        """Fetch REST API taxonomy terms."""
        url = self._builder.build_taxonomy_url(taxonomy)
        return self._http.get(url)

    def _validate_detail_response(self, resp: HttpResponse, identifier: str) -> None:
        """Ensure detail page exists and did not return 404."""
        if resp.status_code == 404:
            raise PropertyNotFoundError(f"Property '{identifier}' was not found.")


class ListingParserBundle:
    """Aggregates search response and metadata parsers."""

    def __init__(
        self,
        search_parser: SearchResponseParser | None = None,
        metadata_parser: MetadataParser | None = None,
    ) -> None:
        """Initialize listing bundle with search and metadata parsers."""
        self._search = search_parser or SearchResponseParser()
        self._metadata = metadata_parser or MetadataParser()

    @property
    def search_parser(self) -> SearchResponseParser:
        """Return search parser."""
        return self._search

    @property
    def metadata_parser(self) -> MetadataParser:
        """Return metadata parser."""
        return self._metadata


class DetailParserBundle:
    """Aggregates detail view parser."""

    def __init__(self, detail_parser: PropertyDetailParser | None = None) -> None:
        """Initialize detail parser."""
        self._detail = detail_parser or PropertyDetailParser()

    @property
    def detail_parser(self) -> PropertyDetailParser:
        """Return detail parser."""
        return self._detail


class RentalParserSuite:
    """Composite suite containing listing and detail parser bundles."""

    def __init__(
        self,
        listing_bundle: ListingParserBundle | None = None,
        detail_bundle: DetailParserBundle | None = None,
    ) -> None:
        """Initialize suite with listing and detail bundles."""
        self._listing = listing_bundle or ListingParserBundle()
        self._detail = detail_bundle or DetailParserBundle()

    @property
    def search_parser(self) -> SearchResponseParser:
        """Access search parser."""
        return self._listing.search_parser

    @property
    def metadata_parser(self) -> MetadataParser:
        """Access metadata parser."""
        return self._listing.metadata_parser

    @property
    def detail_parser(self) -> PropertyDetailParser:
        """Access detail parser."""
        return self._detail.detail_parser
