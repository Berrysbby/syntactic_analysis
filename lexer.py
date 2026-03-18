import re
from pymorphy3 import MorphAnalyzer

from tokens import Token, TokenType


class Lexer:
    def __init__(self):
        self.morph = MorphAnalyzer()

        # Команды (леммы)
        self.commands = {"найти", "показать", "вывести", "представить"}

        # Типы объектов (леммы)
        self.objects = {
            "книга", "статья", "журнал",
            "роман", "повесть", "стихотворение",
            "летопись", "рассказ", "эссе", "сборник",
        }

        # RAW-синонимы/формы, которые лучше ловить без морфологии 
        self._raw_to_token = {
            # Ограничители выборки
            "все": (TokenType.ALL, "весь"),
            "всё": (TokenType.ALL, "весь"),

            "первые": (TokenType.FIRST, "первый"),
            "первую": (TokenType.FIRST, "первый"),
            "первых": (TokenType.FIRST, "первый"),
            "первое": (TokenType.FIRST, "первый"),
            "первый": (TokenType.FIRST, "первый"),
            "первая": (TokenType.FIRST, "первый"),

            "последние": (TokenType.LAST, "последний"),
            "последних": (TokenType.LAST, "последний"),
            "последний": (TokenType.LAST, "последний"),
            "последняя": (TokenType.LAST, "последний"),
            "последнее": (TokenType.LAST, "последний"),
        }

        # Лемма -> тип (всё, что не требует доп. данных)
        self._lemma_to_type = {
            # Временные слова
            "до": TokenType.BEFORE,
            "после": TokenType.AFTER,
            "с": TokenType.FROM,
            "между": TokenType.BETWEEN,

            # Союзы/служебные
            "и": TokenType.AND,
            "по": TokenType.PO,

            # Временные единицы
            "век": TokenType.CENTURY_WORD,
            "год": TokenType.YEAR_WORD,

            # Ограничители выборки (леммы)
            "весь": TokenType.ALL,
            "первый": TokenType.FIRST,
            "последний": TokenType.LAST,
        }

    def tokenize(self, text: str):
        """
        Разбиваем строку на "сырой" список токенов:
        - слова/числа
        - запятые как отдельные токены
        """
        text = text.strip().lower()
        raw_tokens = re.findall(r"\d+|[а-яё-]+|,", text, flags=re.IGNORECASE)

        tokens: list[Token] = []

        for idx, raw in enumerate(raw_tokens):
            if raw == ",":
                tokens.append(Token(TokenType.COMMA, ",", idx, raw))
                continue

            if raw.isdigit():
                tokens.append(Token(TokenType.NUMBER, raw, idx, raw))
                continue

            # 1) Сначала RAW-правила 
            raw_rule = self._raw_to_token.get(raw)
            if raw_rule is not None:
                ttype, value = raw_rule
                tokens.append(Token(ttype, value, idx, raw))
                continue

            # 2) морфология
            lemma = self._lemma(raw)

            # Команды
            if lemma in self.commands:
                tokens.append(Token(TokenType.COMMAND, lemma, idx, raw))
                continue

            # Объекты
            if lemma in self.objects:
                tokens.append(Token(TokenType.OBJECT, lemma, idx, raw))
                continue

            # Лемма-словарь
            ttype = self._lemma_to_type.get(lemma, TokenType.WORD)
            tokens.append(Token(ttype, lemma, idx, raw))

        tokens.append(Token(TokenType.EOF, "EOF", len(raw_tokens), "EOF"))
        return tokens

    def _lemma(self, word: str) -> str:
        # Берём первый разбор
        return self.morph.parse(word)[0].normal_form
