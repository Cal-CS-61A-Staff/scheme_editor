from __future__ import annotations

from enum import Enum, auto
from typing import List

from datamodel import Expression, ValueHolder, Pair
import evaluate_apply
from helper import pair_to_list


class HolderState(Enum):
    UNEVALUATED = auto()
    EVALUATING = auto()
    EVALUATED = auto()
    APPLYING = auto()

class VisualExpression:
    def __init__(self, base_expr: Expression=None):
        self.children = None
        self.value: Expression = None
        self.children: List[Holder] = []
        if base_expr is None:
            return
        if isinstance(base_expr, ValueHolder) or isinstance(base_expr, evaluate_apply.Callable):
            self.value = base_expr
        elif isinstance(base_expr, Pair):
            self.set_entries(pair_to_list(base_expr))
        else:
            raise NotImplementedError(base_expr)

    def set_entries(self, expressions: List[Expression]):
        assert self.value is None, f"self.value of {self} is not None!"
        self.children = [Holder(expression) for expression in expressions]
        return self

    def __repr__(self):
        if self.value is not None:
            return repr(self.value)
        else:
            return "(" + " ".join(map(repr, self.children)) + ")"


class Holder:
    def __init__(self, expr: Expression):
        self.expression = expr
        self.state = HolderState.UNEVALUATED

    def link_visual(self, expr: VisualExpression):
        self.expression = expr
        return expr

    def evaluate(self):
        self.state = HolderState.EVALUATING
        announce("Evaluating", self.expression, Root.root)

    def apply(self):
        self.state = HolderState.APPLYING
        announce("Applying", self.expression, Root.root)

    def complete(self):
        self.state = HolderState.EVALUATED
        announce("Completed", self.expression, Root.root)

    def __repr__(self):
        return repr(self.expression)

silent = False

class Root:
    root: Holder
    @classmethod
    def setroot(cls, root: Holder):
        cls.root = root

def announce(message, local, root):
    if not silent:
        print(f"{message:10}: {repr(local):50} {repr(root):20}")
