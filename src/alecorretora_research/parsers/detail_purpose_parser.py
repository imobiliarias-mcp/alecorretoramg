"""Transaction-purpose extraction from property detail taxonomy."""

import re

from bs4 import BeautifulSoup, Tag


def extract_property_purpose(soup: BeautifulSoup, title: str, description: str) -> str:
    """Return the page's explicit purpose or wording fallback; unknown returns empty."""
    fields = soup.find_all(class_="jet-listing-dynamic-terms")
    purposes = (_purpose_from_terms(field) for field in fields)
    purpose = next((value for value in purposes if value), "")
    if purpose:
        return purpose
    text = f"{title} {description}"
    if re.search(r"\balug\w*|\blocação\b", text, re.IGNORECASE):
        return "Alugar"
    if re.search(r"\bvend\w*|\bcomprar\b", text, re.IGNORECASE):
        return "Venda"
    return ""


def _purpose_from_terms(field: Tag) -> str:
    """Read the current property's labelled purpose, excluding unrelated widgets."""
    if _is_excluded_field(field):
        return ""
    prefix = field.find(class_="jet-listing-dynamic-terms__prefix")
    if prefix is None:
        return ""
    label = prefix.get_text(strip=True)
    if label.casefold().rstrip(":") != "finalidade":
        return ""
    term = field.find(class_="jet-listing-dynamic-terms__link")
    if term is None:
        return ""
    return term.get_text(strip=True)


def _is_excluded_field(field: Tag) -> bool:
    """Identify transaction fields inside navigation or related properties."""
    if field.find_parent(class_="jet-listing-grid"):
        return True
    return bool(field.find_parent(["header", "footer"]))
