from ast_nodes import Node
from tokens import TokenType
from lexer import Lexer

class ParserError(Exception):
    pass

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def current(self):
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None

    def advance(self):
        self.pos += 1

    def expect(self, token_type, message):
        tok = self.current()
        if tok is None:
            raise ParserError(f"{message}. Ошибка: конец запроса")
        if tok.type != token_type:
            token_raw = getattr(tok, "raw", tok.value)
            token_pos = getattr(tok, "position", "?")
            raise ParserError(f"{message}. Ошибка на токене '{token_raw}' (позиция {token_pos})")
        self.pos += 1
        return tok

    def parse(self):
        node = Node("Query")
        node.add_child(self.parse_command())
        node.add_child(self.parse_object_clause())

        filters = self.parse_filters()
        if filters:
            node.add_child(filters)
        return node

    def parse_command(self):
        tok = self.current()
        if tok and tok.type == TokenType.COMMAND:
            self.advance()
            return Node("Command", tok.value)
        token_raw = getattr(tok, "raw", "EOF") if tok else "EOF"
        token_pos = getattr(tok, "position", self.pos) if tok else self.pos
        raise ParserError(
            f"Ожидалась команда (найди/покажи/выведи/представь). "
            f"Ошибка на токене '{token_raw}' (позиция {token_pos})"
        )

    def parse_object_clause(self):
        node = Node("ObjectClause")

        # 1) Опционально: "все"
        if self.current() and self.current().type == TokenType.ALL:
            self.advance()
            node.add_child(Node("All", "все"))

        # 2) Опционально: "первые N"
        if self.current() and self.current().type == TokenType.FIRST:
            self.advance()
            n_tok = self.expect(TokenType.NUMBER, "После 'первые' ожидалось число")
            first_node = Node("FirstN")
            first_node.add_child(Node("Number", n_tok.value))
            node.add_child(first_node)

        # 3) Обязательный объект
        obj_tok = self.expect(TokenType.OBJECT, "Ожидался тип объекта (книги/романы/летописи/...)")
        objects_node = Node("Objects")
        objects_node.add_child(Node("Object", obj_tok.value))

        # 4) Доп. объекты через запятую: "романы, повести, ..."
        while self.current() and self.current().type == TokenType.COMMA:
            self.advance()
            next_obj = self.expect(TokenType.OBJECT, "Ожидался объект после запятой")
            objects_node.add_child(Node("Object", next_obj.value))

        node.add_child(objects_node)

        # 5) Опционально: авторы/имена после объекта: "Толстого и Достоевского"
        #    Разбираем цепочку WORD (AND WORD)*
        if self.current() and self.current().type == TokenType.WORD:
            authors = Node("Authors")
            w = self.expect(TokenType.WORD, "Ожидалось имя автора")
            authors.add_child(Node("Author", w.value))

            while self.current() and self.current().type == TokenType.AND:
                self.advance()
                w = self.expect(TokenType.WORD, "Ожидалось имя автора после 'и'")
                authors.add_child(Node("Author", w.value))

            node.add_child(authors)

        return node

    def parse_filters(self):
        next_tok = self.current()
        if not next_tok:
            return None

        node = Node("Filters")

        while next_tok and next_tok.type != TokenType.EOF:
            if next_tok.type == TokenType.PO:
                self.advance()
                word_tok = self.expect(TokenType.WORD, "После 'по' ожидалась тема")
                node.add_child(Node("Topic", word_tok.value))

            elif next_tok.type == TokenType.NUMBER:
                num_tok = self.current()
                self.advance()
                year_tok = self.current()
                if year_tok and year_tok.type in (TokenType.YEAR_WORD, TokenType.CENTURY_WORD):
                    self.advance()
                    node.add_child(Node("Year", num_tok.value))
                else:
                    node.add_child(Node("Number", num_tok.value))

            elif next_tok.type == TokenType.FROM:
                # с <год> по <год> — оставляем как строгую форму (как у тебя сейчас)
                self.advance()
                start_tok = self.expect(TokenType.NUMBER, "После 'с' ожидалось число")
                self.expect(TokenType.PO, "После начального года ожидалось 'по'")
                end_tok = self.expect(TokenType.NUMBER, "После 'по' ожидалось число")
                range_node = Node("Range")
                range_node.add_child(Node("Start", start_tok.value))
                range_node.add_child(Node("End", end_tok.value))
                node.add_child(range_node)

            elif next_tok.type == TokenType.BETWEEN:
                self.advance()
                start_tok = self.expect(TokenType.NUMBER, "После 'между' ожидалось число")
                self.expect(TokenType.AND, "После числа ожидалось 'и'")
                end_tok = self.expect(TokenType.NUMBER, "После 'и' ожидалось число")
                range_node = Node("Range")
                range_node.add_child(Node("Start", start_tok.value))
                range_node.add_child(Node("End", end_tok.value))
                node.add_child(range_node)

            elif next_tok.type in (TokenType.BEFORE, TokenType.AFTER):
                kind = next_tok.type
                self.advance()
                num_tok = self.expect(TokenType.NUMBER, f"После '{kind.name.lower()}' ожидалось число")
                node.add_child(Node(kind.name.title(), num_tok.value))

            elif next_tok.type == TokenType.FROM:
                # с <год> по <год>  (диапазон)
                # или с <год>       (начиная с <год>)
                self.advance()
                start_tok = self.expect(TokenType.NUMBER, "После 'с' ожидалось число")

                if self.current() and self.current().type == TokenType.PO:
                    self.advance()
                    end_tok = self.expect(TokenType.NUMBER, "После 'по' ожидалось число")
                    range_node = Node("Range")
                    range_node.add_child(Node("Start", start_tok.value))
                    range_node.add_child(Node("End", end_tok.value))
                    node.add_child(range_node)
                else:
                    # трактуем "с 2018" как "после 2018" / "начиная с 2018"
                    node.add_child(Node("After", start_tok.value))
            else:
                break

            next_tok = self.current()

        return node if node.children else None