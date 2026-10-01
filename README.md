# Alê Corretora MG — Central Rental Research MCP Provider

Reverse-engineered rental search engine and API client for **Alê Corretora MG** (`https://alecorretoramg.com.br/`).

Engineered as a pluggable adapter for the **Central Rental Research MCP (Model Context Protocol)** server following **SOLID**, **Clean Code**, **Object Calisthenics**, and **Design Patterns** in Python.

---

## 📚 Documentation

- **[Reverse Engineering API Specification](file:///home/samuelcaldas/repos/imobiliarias/alecorretoramg/docs/api-research.md)** (`docs/api-research.md`): Complete endpoint contracts, payload schemas, query parameters, DOM selectors, and JetSmartFilters architecture.
- **[Research Plan & Findings Report](file:///home/samuelcaldas/repos/imobiliarias/alecorretoramg/scripts/research-plan.md)** (`scripts/research-plan.md`): Reverse-engineering methodology, parameter probing matrix, software architecture design, and verification log.

---

## ⚡ Quickstart

### Run Automated Tests
```bash
uv run pytest -v tests
```

### Run Live Research Verification
```bash
python3 scripts/verify_research.py
```

### Python MCP Client Usage
```python
from alecorretora_research import AleCorretoraRentalClient, PropertyType

client = AleCorretoraRentalClient()

# 1. Search rentals in Timóteo with 2 bedrooms
results = client.search_rentals(city_id="24", bedrooms=2)
for item in results:
    print(f"[{item.property_id}] Ref: {item.code} | {item.title} | {item.price_formatted}")

# 2. Get property detail and photo gallery
detail = client.get_details("11217")
print(f"Title: {detail.title} | Price: {detail.price_formatted}")
print(f"Total photos: {len(detail.gallery)}")

# 3. Discover portal locations
locations = client.get_locations()
print(f"Indexed cities: {len(locations.cities)}")
```

---

## 🏛️ Code Architecture & Standards Compliance

- **Priority Order**: Correctness first, modularity second, style principles third.
- **No `else` Keyword**: 100% eliminated using guard clauses, early returns, and polymorphic handlers.
- **Single Level of Indentation**: All methods adhere to at most 1 indent level.
- **Wrapped Primitives**: Domain concepts (`PriceRange`, `RoomCount`, `PageNumber`, `PropertyCode`) are immutable Value Objects.
- **First-Class Collections**: `ListingCollection`, `PhotoGallery`, `CityCatalog`, `NeighborhoodCatalog`, and `LocationCatalog` wrap items without leaking raw mutable collections.
- **Size Limits**: Functions ≤ 15 lines, Classes ≤ 100 lines, Modules < 200 lines.
- **Instance Variables**: All classes hold at most 2 instance variables (composed via collaborator bundles).
- **Zero Abbreviations**: Clear, descriptive domain naming across all modules.
