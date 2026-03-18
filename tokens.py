from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto


class TokenType(Enum):
    # Спец
    EOF = auto()

    # Базовые
    COMMAND = auto()
    ALL = auto()
    FIRST = auto()
    LAST = auto()

    OBJECT = auto()

    NUMBER = auto()
    WORD = auto()

    COMMA = auto()
    AND = auto()

    BEFORE = auto()       # до
    AFTER = auto()        # после
    FROM = auto()         # с
    BETWEEN = auto()      # между

    PO = auto()           # "по" 
    CENTURY_WORD = auto() # век / века
    YEAR_WORD = auto()    # год / года


@dataclass(frozen=True)
class Token:
    """
    Лексема.
    position - индекс токена в строке 
    raw      - исходное слово
    value    - нормализованное значение (лемма или число)
    """
    type: TokenType
    value: str
    position: int
    raw: str

    def __repr__(self) -> str:
        return f"Token(type={self.type.name}, value='{self.value}', pos={self.position}, raw='{self.raw}')"
