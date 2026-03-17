def print_result(query, success, tree=None, error=None):
    print("=" * 80)
    print(f"Запрос: {query}")
    print()

    if success:
        print("Результат синтаксического анализа: УСПЕХ")
        if tree:
            print("\nДерево разбора:")
            print(tree.pretty())
    else:
        print("Результат синтаксического анализа: ОШИБКА")
        print(f"Диагностика: {error}")