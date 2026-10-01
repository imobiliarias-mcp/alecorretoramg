"""Infrastructure layer exports for Alê Corretora MG research."""

from alecorretora_research.infrastructure.http_client import (
    HttpClientProtocol,
    HttpResponse,
    HttpxHttpClient,
    InvalidCriteriaError,
    PropertyNotFoundError,
    RentalResearchError,
    SearchRequestError,
)
from alecorretora_research.infrastructure.payload_builder import RequestPayloadBuilder

__all__ = [
    "HttpClientProtocol",
    "HttpResponse",
    "HttpxHttpClient",
    "InvalidCriteriaError",
    "PropertyNotFoundError",
    "RentalResearchError",
    "RequestPayloadBuilder",
    "SearchRequestError",
]
