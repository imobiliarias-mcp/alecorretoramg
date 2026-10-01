"""Domain enumerations for Alê Corretora MG portal."""

from enum import Enum


class TransactionType(str, Enum):
    """Transaction purpose taxonomy values."""

    ALUGAR = "21"
    COMPRAR = "20"


class PropertyType(str, Enum):
    """Property category taxonomy values."""

    TODOS = ""
    APARTAMENTO = "8"
    CASA = "7"
    CASA_GEMINADA = "32"
    CHACARA = "56"
    COBERTURA = "50"
    LOTE = "55"
    LOJA_COMERCIAL = "34"
    SALA_COMERCIAL = "33"
    PREDIO = "314"
    AREA = "444"
