class ParseError(Exception):
    def __init__(self, message, token=None):
        self.message = message
        self.token = token
        super().__init__(self.__str__())

    def __str__(self):
        if self.token is None:
            return self.message
        return f"{self.message}. Ошибка на токене '{self.token.raw}' (позиция {self.token.position})"