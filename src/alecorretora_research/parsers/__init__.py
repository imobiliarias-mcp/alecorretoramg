"""Parsers layer package exports for Alê Corretora MG research."""

from alecorretora_research.parsers.detail_parser import PropertyDetailParser
from alecorretora_research.parsers.feature_extractor import CardFeatureExtractor
from alecorretora_research.parsers.metadata_parser import MetadataParser
from alecorretora_research.parsers.search_parser import SearchResponseParser

__all__ = [
    "CardFeatureExtractor",
    "MetadataParser",
    "PropertyDetailParser",
    "SearchResponseParser",
]
