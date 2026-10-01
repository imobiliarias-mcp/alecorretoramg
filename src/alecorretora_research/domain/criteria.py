"""Search criteria domain models and query parameter mapping."""

from dataclasses import dataclass, field
from alecorretora_research.domain.enums import PropertyType, TransactionType
from alecorretora_research.domain.values import (
    PageNumber,
    PriceRange,
    PropertyCode,
    RoomCount,
)


@dataclass(frozen=True)
class FilterCriteria:
    """Encapsulates taxonomy and metadata search filters."""

    transaction_type: TransactionType = TransactionType.ALUGAR
    property_type: PropertyType = PropertyType.TODOS
    city_id: str | None = None
    neighborhood_id: str | None = None
    bedrooms: RoomCount | None = None
    bathrooms: RoomCount | None = None
    price_range: PriceRange | None = None
    code: PropertyCode | None = None

    def build_query_dict(self) -> dict[str, str]:
        """Convert domain filters to JetSmartFilters query parameters."""
        query: dict[str, str] = {}
        if self.transaction_type.value:
            query["_tax_query_finalidade"] = self.transaction_type.value
        if self.property_type.value:
            query["_tax_query_tipo-de-imovel"] = self.property_type.value
        if self.city_id:
            query["_tax_query_cidade"] = self.city_id
        if self.neighborhood_id:
            query["_tax_query_bairro"] = self.neighborhood_id
        if self.bedrooms is not None:
            query["_meta_query_quartos"] = self.bedrooms.to_query_value()
        if self.bathrooms is not None:
            query["_meta_query_banheiros"] = self.bathrooms.to_query_value()
        if self.price_range is not None:
            price_val = self.price_range.to_query_value()
            if price_val:
                query["_meta_query_preco|range"] = price_val
        if self.code is not None:
            query["_meta_query_codigo-do-imovel"] = self.code.value
        return query


@dataclass(frozen=True)
class PaginationCriteria:
    """Encapsulates pagination control."""

    page: PageNumber = field(default_factory=PageNumber)


@dataclass(frozen=True)
class SearchCriteria:
    """Aggregate domain search request combining filters and pagination."""

    filters: FilterCriteria = field(default_factory=FilterCriteria)
    pagination: PaginationCriteria = field(default_factory=PaginationCriteria)

    @classmethod
    def create_rental(
        cls,
        city_id: str | None = None,
        neighborhood_id: str | None = None,
        property_type: PropertyType = PropertyType.TODOS,
        bedrooms: int | None = None,
        bathrooms: int | None = None,
        min_price: int | None = None,
        max_price: int | None = None,
        code: str | None = None,
        page: int = 1,
    ) -> "SearchCriteria":
        """Factory method constructing rental criteria with primitive inputs."""
        price_range = PriceRange(min_price, max_price) if (min_price or max_price) else None
        bedroom_vo = RoomCount(bedrooms) if bedrooms is not None else None
        bathroom_vo = RoomCount(bathrooms) if bathrooms is not None else None
        code_vo = PropertyCode(code) if code else None

        filters = FilterCriteria(
            transaction_type=TransactionType.ALUGAR,
            property_type=property_type,
            city_id=city_id,
            neighborhood_id=neighborhood_id,
            bedrooms=bedroom_vo,
            bathrooms=bathroom_vo,
            price_range=price_range,
            code=code_vo,
        )
        pagination = PaginationCriteria(page=PageNumber(page))
        return cls(filters=filters, pagination=pagination)

    def to_query_dict(self) -> dict[str, str]:
        """Delegate query construction to filter criteria."""
        return self.filters.build_query_dict()

    @property
    def page_number(self) -> int:
        """Return the current 1-indexed page number."""
        return self.pagination.page.value
