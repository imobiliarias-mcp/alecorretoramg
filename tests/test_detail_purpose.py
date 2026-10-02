"""Regression tests for explicit property transaction taxonomy."""

import pytest

from alecorretora_research.parsers.detail_parser import PropertyDetailParser

PURPOSE_FIELD = (
    '<div class="jet-listing jet-listing-dynamic-terms">'
    '<span class="jet-listing-dynamic-terms__prefix">Finalidade: </span>'
    '<a class="jet-listing-dynamic-terms__link">{purpose}</a></div>'
)


@pytest.mark.parametrize("purpose", ("Alugar", "Venda"))
def test_explicit_purpose_overrides_description_words(purpose):
    """The published transaction takes precedence over description keywords."""
    field = PURPOSE_FIELD.format(purpose=purpose)
    html = f'<h1>Apartamento</h1>{field}'
    html += '<div class="elementor-widget-text-editor">Preço do aluguel sob consulta.</div>'
    detail = PropertyDetailParser().parse(html)
    assert detail.purpose == purpose


def test_related_listing_does_not_supply_property_purpose():
    """A related property's taxonomy cannot classify the current property."""
    field = PURPOSE_FIELD.format(purpose="Alugar")
    html = f'<h1>Apartamento</h1><div class="jet-listing-grid">{field}</div>'
    detail = PropertyDetailParser().parse(html)
    assert detail.purpose == ""


def test_missing_purpose_is_not_assumed_to_be_sale():
    """Missing transaction information remains unknown rather than fabricated."""
    detail = PropertyDetailParser().parse('<h1>Apartamento</h1>')
    assert detail.purpose == ""


def test_uppercase_rental_description_remains_supported():
    """Unambiguous rental wording can classify pages without a taxonomy field."""
    html = '<h1>Apartamento</h1><div class="elementor-widget-text-editor">ALUGO APARTAMENTO</div>'
    detail = PropertyDetailParser().parse(html)
    assert detail.purpose == "Alugar"
