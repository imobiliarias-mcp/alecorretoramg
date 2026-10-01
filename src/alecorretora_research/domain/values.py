"""Domain value objects with strict input validation."""

from dataclasses import dataclass


@dataclass(frozen=True)
class PriceRange:
    """Encapsulates numeric minimum and maximum price constraints in BRL."""

    min_price: int | None = None
    max_price: int | None = None

    def __post_init__(self) -> None:
        """Validate price boundaries upon instantiation."""
        if self.min_price is not None and self.min_price < 0:
            raise ValueError(f"Minimum price cannot be negative: {self.min_price}")
        if self.max_price is not None and self.max_price < 0:
            raise ValueError(f"Maximum price cannot be negative: {self.max_price}")
        if (
            self.min_price is not None
            and self.max_price is not None
            and self.min_price > self.max_price
        ):
            raise ValueError(
                f"Minimum price ({self.min_price}) cannot exceed maximum price ({self.max_price})"
            )

    def to_query_value(self) -> str | None:
        """Format as JetSmartFilters range string '{min}_{max}'."""
        if self.min_price is None and self.max_price is None:
            return None
        lower_bound = self.min_price if self.min_price is not None else 0
        upper_bound = self.max_price if self.max_price is not None else 5000000
        return f"{lower_bound}_{upper_bound}"


@dataclass(frozen=True)
class RoomCount:
    """Encapsulates room or bathroom count constraint."""

    count: int

    def __post_init__(self) -> None:
        """Validate count boundary."""
        if self.count < 0:
            raise ValueError(f"Room count cannot be negative: {self.count}")

    def to_query_value(self) -> str:
        """Format as query parameter string."""
        if self.count >= 4:
            return "4"
        return str(self.count)


@dataclass(frozen=True)
class PageNumber:
    """Encapsulates 1-indexed pagination number."""

    value: int = 1

    def __post_init__(self) -> None:
        """Validate that page number is positive."""
        if self.value < 1:
            raise ValueError(f"Page number must be at least 1, received: {self.value}")


@dataclass(frozen=True)
class PropertyCode:
    """Encapsulates clean property reference code."""

    value: str

    def __post_init__(self) -> None:
        """Validate non-empty code value."""
        stripped = self.value.strip()
        if not stripped:
            raise ValueError("Property code cannot be empty.")
        object.__setattr__(self, "value", stripped)
