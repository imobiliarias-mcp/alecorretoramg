"""Card feature and specification extractor for search listing cards."""

import re
from typing import Any
from bs4 import BeautifulSoup, Tag
from alecorretora_research.domain.listing import ListingSummary


class CardFeatureExtractor:
    """Extracts domain listing summary attributes from card DOM elements."""

    def extract(self, card: Tag) -> ListingSummary:
        """Parse card tag into ListingSummary."""
        post_id = card.get("data-post-id", "")
        url = self._extract_url(card)
        thumb = self._extract_thumbnail(card)
        code = self._extract_code(card)
        purpose = self._extract_purpose(card)
        prop_type = self._extract_property_type(card)
        bairro = self._extract_neighborhood(card)
        cidade = self._extract_city(card)
        price = self._extract_price(card)
        specs = self._extract_specs(card)

        return ListingSummary(
            property_id=post_id,
            url=url,
            code=code,
            title=f"{prop_type} em {bairro}, {cidade}".strip(),
            purpose=purpose,
            property_type=prop_type,
            neighborhood=bairro,
            city=cidade,
            price_formatted=price,
            bedrooms=specs.get("bedrooms"),
            bathrooms=specs.get("bathrooms"),
            parking_spaces=specs.get("parking"),
            area=specs.get("area"),
            thumbnail_url=thumb,
        )

    def _extract_url(self, card: Tag) -> str:
        """Extract property URL."""
        overlay = card.find(class_="jet-engine-listing-overlay-wrap")
        if overlay and overlay.get("data-url"):
            return overlay.get("data-url", "")
        link = card.find("a", href=lambda h: h and "/imoveis/" in h)
        return link.get("href", "") if link else ""

    def _extract_thumbnail(self, card: Tag) -> str | None:
        """Extract background thumbnail image URL."""
        style = card.find("style")
        if style and style.string:
            match = re.search(r'background-image:url\(\"([^\"]+)\"\)', style.string)
            if match:
                return match.group(1)
        img = card.find("img")
        return img.get("src") if img else None

    def _extract_code(self, card: Tag) -> str:
        """Extract reference code like '0473'."""
        for heading in card.find_all(class_="elementor-heading-title"):
            match = re.search(r"Cod\.\s*(\d+)", heading.get_text(strip=True))
            if match:
                return match.group(1)
        return ""

    def _extract_purpose(self, card: Tag) -> str:
        """Extract transaction purpose (Alugar/Comprar)."""
        headings = card.find_all(class_="elementor-heading-title")
        if headings:
            first_text = headings[0].get_text(strip=True)
            if first_text in ["Alugar", "Comprar"]:
                return first_text
        return "Alugar"

    def _extract_property_type(self, card: Tag) -> str:
        """Extract property type title."""
        headings = card.find_all(class_="elementor-heading-title")
        if len(headings) >= 3:
            return headings[2].get_text(strip=True)
        if len(headings) == 2:
            return headings[1].get_text(strip=True)
        return "Imóvel"

    def _extract_neighborhood(self, card: Tag) -> str:
        """Extract neighborhood from dynamic terms."""
        bairro_link = card.find("a", href=lambda h: h and "/bairro/" in h)
        return bairro_link.get_text(strip=True) if bairro_link else ""

    def _extract_city(self, card: Tag) -> str:
        """Extract city from dynamic terms."""
        cidade_link = card.find("a", href=lambda h: h and "/cidade/" in h)
        return cidade_link.get_text(strip=True) if cidade_link else ""

    def _extract_price(self, card: Tag) -> str:
        """Extract formatted price."""
        price_el = card.find(class_="jet-listing-dynamic-field__content")
        return price_el.get_text(strip=True) if price_el else ""

    def _extract_specs(self, card: Tag) -> dict[str, Any]:
        """Extract bedrooms, bathrooms, parking, and area from icon list."""
        specs: dict[str, Any] = {}
        for idx, item in enumerate(card.find_all(class_="elementor-icon-list-item")):
            text = item.get_text(strip=True)
            self._assign_spec_by_index(specs, idx, text)
        return specs

    def _assign_spec_by_index(self, specs: dict[str, Any], idx: int, text: str) -> None:
        """Assign specs by known card layout ordering or label."""
        if "m²" in text:
            specs["area"] = text
            return
        if not text.isdigit():
            return
        val = int(text)
        if idx == 0:
            specs["bedrooms"] = val
        elif idx == 1:
            specs["bathrooms"] = val
        elif idx == 2:
            specs["parking"] = val
