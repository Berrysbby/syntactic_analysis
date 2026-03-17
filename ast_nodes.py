import subprocess
from collections import deque

class Node:
    """
    Узел дерева разбора.
    name  - имя узла
    value - значение, если это лист
    children - список дочерних узлов
    """
    def __init__(self, name, value=None, children=None):
        self.name = name
        self.value = value
        self.children = children if children is not None else []

    def add_child(self, node):
        self.children.append(node)

    def add(self, node):
        self.children.append(node)

    def pretty(self, level=0):
        indent = "  " * level
        if self.value is not None:
            result = f"{indent}{self.name}: {self.value}\n"
        else:
            result = f"{indent}{self.name}\n"
        for child in self.children:
            result += child.pretty(level + 1)
        return result

    def __str__(self):
        return self.pretty()

    def __repr__(self):
        return self.pretty()
