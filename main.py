from lexer import Lexer
from parser import Parser
from errors import ParseError
from utils import print_result


def process_query(query: str):
    lexer = Lexer()
    tokens = lexer.tokenize(query)

    # Технический вывод (как у тебя было)
    for t in tokens:
        print(f"raw='{t.raw}' type='{t.type}' value='{t.value}'")

    tree = Parser(tokens).parse()
    return tokens, tree


def main():
    input_file = "input.txt"

    try:
        with open(input_file, "r", encoding="utf-8") as f:
            queries = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"Файл {input_file} не найден.")
        return

    for query in queries:
        try:
            tokens, tree = process_query(query)

            print("\nЛексемы:")
            for t in tokens:
                print(f"  {t}")

            print_result(query, True, tree=tree)

        except (ParseError, Exception) as e:
            print_result(query, False, error=e)

        print()


if __name__ == "__main__":
    print("main() запущен")
    main()
