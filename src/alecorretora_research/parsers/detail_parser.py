"""Parser for property detail HTML pages."""

import re
from typing import Any
from bs4 import BeautifulSoup
from alecorretora_research.domain.property import (
    PhotoGallery,
    PropertyDetail,
    PropertyLocation,
    PropertySpecs,
)


class PropertyDetailParser:
    """Extracts PropertyDetail domain model from full property page HTML."""

    def parse(
        self,
        html_content: str,
        property_id: str = "",
        canonical_url: str = "",
    ) -> PropertyDetail:
        """Parse detail page markup into PropertyDetail domain entity."""
        soup = BeautifulSoup(html_content, "html.parser")
        title = self._extract_title(soup)
        code = self._extract_code(soup)
        price = self._extract_price(soup)
        desc = self._extract_description(soup)
        specs = self._extract_specs(soup)
        location = self._extract_location(soup, desc)
        gallery = self._extract_gallery(soup)

        return PropertyDetail(
            property_id=property_id or code,
            url=canonical_url,
            code=code,
            title=title,
            purpose="Alugar" if "Alug" in title or "Alug" in desc else "Venda",
            price_formatted=price,
            description=desc,
            location=location,
            specs=specs,
            gallery=gallery,
        )

    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract main property title."""
        h1 = soup.find("h1")
        return h1.get_text(strip=True) if h1 else ""

    def _extract_code(self, soup: BeautifulSoup) -> str:
        """Extract property reference code."""
        for heading in soup.find_all(class_="elementor-heading-title"):
            match = re.search(r"Código do Imóvel:\s*([A-Za-z0-9_-]+)", heading.get_text())
            if match:
                return match.group(1)
        fallback = re.search(r"Código do Imóvel:\s*([A-Za-z0-9_-]+)", soup.get_text())
        if fallback:
            return fallback.group(1)
        return ""

    def _extract_price(self, soup: BeautifulSoup) -> str:
        """Extract formatted price."""
        field = soup.find(class_="jet-listing-dynamic-field")
        return field.get_text(strip=True) if field else ""

    def _extract_description(self, soup: BeautifulSoup) -> str:
        """Extract property description text."""
        desc_el = soup.find(class_="elementor-widget-text-editor")
        return desc_el.get_text("\n", strip=True) if desc_el else ""

    def _extract_location(self, soup: BeautifulSoup, desc: str) -> PropertyLocation:
        """Extract property location from description or address elements."""
        match = re.search(r"bairro\s+([^,]+),\s*em\s+([^/]+)/([A-Z]{2})", desc, re.I)
        if match:
            return PropertyLocation(
                neighborhood=match.group(1).strip(),
                city=match.group(2).strip(),
                state=match.group(3).strip(),
            )
        match_simple = re.search(r"bairro\s+([A-Za-zÀ-ÿ\s]+)\s+em\s+([A-Za-zÀ-ÿ\s]+)", desc, re.I)
        if match_simple:
            return PropertyLocation(
                neighborhood=match_simple.group(1).strip(),
                city=match_simple.group(2).strip(),
            )
        return PropertyLocation(neighborhood="", city="Timóteo")

    def _extract_specs(self, soup: BeautifulSoup) -> PropertySpecs:
        """Extract physical specifications excluding headers, footers, and grids."""
        specs_dict: dict[str, Any] = {}
        for widget in soup.find_all(attrs={"data-widget_type": "icon-list.default"}):
            if self._is_excluded_widget(widget):
                continue
            self._parse_icon_widget_items(widget, specs_dict)

        return PropertySpecs(
            bedrooms=specs_dict.get("bedrooms"),
            bathrooms=specs_dict.get("bathrooms"),
            parking_spaces=specs_dict.get("parking"),
            area=specs_dict.get("area"),
        )

    def _is_excluded_widget(self, widget: Any) -> bool:
        """Determine if widget is inside header, footer, or similar listings."""
        if widget.find_parent(class_="jet-listing-grid"):
            return True
        if widget.find_parent("header") or widget.find_parent("footer"):
            return True
        return False

    def _parse_icon_widget_items(self, widget: Any, specs_dict: dict[str, Any]) -> None:
        """Parse individual items within property icon list."""
        for item in widget.find_all(class_="elementor-icon-list-item"):
            text = item.get_text(" ", strip=True)
            self._match_spec_item(text, specs_dict)

    def _match_spec_item(self, text: str, specs_dict: dict[str, Any]) -> None:
        """Extract bedroom, bathroom, parking, or area from item text."""
        if "Quarto" in text:
            m = re.search(r"Quartos?:\s*(\d+)", text)
            if m:
                specs_dict["bedrooms"] = int(m.group(1))
        elif "Banheiro" in text:
            m = re.search(r"Banheiros?:\s*(\d+)", text)
            if m:
                specs_dict["bathrooms"] = int(m.group(1))
        elif "Vaga" in text or "Garagem" in text:
            m = re.search(r"(?:Vagas?|Garagem):\s*(\d+)", text)
            if m:
                specs_dict["parking"] = int(m.group(1))
        elif "Área" in text or "m²" in text:
            specs_dict["area"] = text

    def _extract_gallery(self, soup: BeautifulSoup) -> PhotoGallery:
        """Extract high-resolution photo URLs from carousel widget."""
        carousel = soup.find(attrs={"data-widget_type": "image-carousel.default"})
        if not carousel:
            return PhotoGallery([])
        photos: list[str] = []
        for anchor in carousel.find_all("a"):
            href = anchor.get("href", "").strip()
            if href and ("jpg" in href or "png" in href or "jpeg" in href):
                photos.append(href)
        return PhotoGallery(photos)
