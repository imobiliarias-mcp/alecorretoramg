#!/usr/bin/env python3
"""Verification runner demonstrating reverse-engineered endpoints and MCP client."""

import sys
from pathlib import Path

# Ensure src is in python path
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR / "src"))

from alecorretora_research import (
    AleCorretoraRentalClient,
    PriceRange,
    PropertyType,
    RoomCount,
    SearchCriteria,
)


def run_target_rental_search(client: AleCorretoraRentalClient) -> None:
    """Execute reproduction of user prompt target search (Rentals on todos-os-imoveis)."""
    print("--- 1. Target URL Rental Search (Alugar / Todos os Imóveis) ---")
    results = client.search_rentals()
    print(f"Total matching rentals found: {results.total_found}")
    for item in results:
        print(f"  [{item.property_id}] Ref: {item.code} | {item.title} | {item.price_formatted} | {item.neighborhood}, {item.city}")
        print(f"    Link: {item.url}")


def run_bedroom_filtered_search(client: AleCorretoraRentalClient) -> None:
    """Execute filtered search by bedroom count."""
    print("\n--- 2. Filtered Rental Search (2 Bedrooms) ---")
    results = client.search_rentals(bedrooms=2)
    print(f"Total 2-bedroom rentals: {len(results)}")
    for item in results:
        print(f"  [{item.property_id}] Ref: {item.code} | {item.title} | {item.price_formatted}")
        print(f"    Link: {item.url}")


def run_price_range_search(client: AleCorretoraRentalClient) -> None:
    """Execute filtered search by price range."""
    print("\n--- 3. Filtered Rental Search (Price: R$ 700 to R$ 1.500) ---")
    results = client.search_rentals(min_price=700, max_price=1500)
    print(f"Total rentals in price range: {len(results)}")
    for item in results:
        print(f"  [{item.property_id}] Ref: {item.code} | {item.title} | {item.price_formatted}")
        print(f"    Link: {item.url}")


def run_code_search(client: AleCorretoraRentalClient) -> None:
    """Execute reference code search."""
    print("\n--- 4. Code Search (Ref: 0473) ---")
    results = client.search_rentals(code="0473")
    print(f"Total matching properties: {len(results)}")
    for item in results:
        print(f"  [{item.property_id}] Ref: {item.code} | {item.title} | {item.price_formatted}")
        print(f"    Link: {item.url}")


def run_detail_retrieval(client: AleCorretoraRentalClient) -> None:
    """Retrieve details for sample rental property (ID 11217)."""
    print("\n--- 5. Property Detail Retrieval (ID: 11217 / Ref: 0473) ---")
    detail = client.get_details("11217")
    print(f"Title: {detail.title}")
    print(f"Reference Code: {detail.code}")
    print(f"Price: {detail.price_formatted}")
    print(f"Location: {detail.location.neighborhood}, {detail.location.city} - {detail.location.state}")
    print(f"Specs: {detail.specs.bedrooms} dorm, {detail.specs.bathrooms} banheiro, Área: {detail.specs.area}")
    print(f"Photos in Gallery: {len(detail.gallery)}")
    for idx, photo_url in enumerate(list(detail.gallery)[:3]):
        print(f"  Photo {idx + 1}: {photo_url}")


def run_locations_discovery(client: AleCorretoraRentalClient) -> None:
    """Discover portal cities and neighborhoods."""
    print("\n--- 6. Portal Location Catalog Discovery ---")
    catalog = client.get_locations()
    print(f"Total cities indexed: {len(catalog.cities)}")
    timoteo = catalog.cities.find_by_name("timóteo")
    if timoteo:
        print(f"City found: '{timoteo.name}' (ID: {timoteo.city_id})")
    print(f"Total neighborhoods indexed: {len(catalog.neighborhoods)}")


def main() -> None:
    """Run all verification steps."""
    print("=== Starting Alê Corretora MG Research Verification ===")
    client = AleCorretoraRentalClient()
    run_target_rental_search(client)
    run_bedroom_filtered_search(client)
    run_price_range_search(client)
    run_code_search(client)
    run_detail_retrieval(client)
    run_locations_discovery(client)
    print("\n=== All Verification Steps Completed Successfully ===")


if __name__ == "__main__":
    main()
