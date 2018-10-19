from __future__ import annotations

from enum import Enum, auto
from typing import List, Union
from uuid import uuid4

from datamodel import Expression, ValueHolder, Pair, Nil
import evaluate_apply
from helper import pair_to_list


class HolderState(Enum):
    UNEVALUATED = auto()
    EVALUATING = auto()
    EVALUATED = auto()
    APPLYING = auto()


class VisualExpression:
    def __init__(self, base_expr: Expression = None, true_base_expr: Expression = None):
        self.children = None
        self.display_value = base_expr
        self.base_expr = base_expr if true_base_expr is None else true_base_expr
        self.value: Expression = None
        self.children: List[Holder] = []
        self.id = uuid4()
        if base_expr is None:
            return
        if isinstance(base_expr, ValueHolder) or isinstance(base_expr, evaluate_apply.Callable) or base_expr == Nil:
            self.value = base_expr
        elif isinstance(base_expr, Pair):
            self.set_entries(pair_to_list(base_expr))
        else:
            raise NotImplementedError(base_expr)

    def set_entries(self, expressions: List[Expression]):
        self.value = None
        self.children = [Holder(expression) for expression in expressions]
        return self

    def __repr__(self):
        if self.value is not None:
            return repr(self.value)
        return repr(self.display_value)


class Holder:
    def __init__(self, expr: Expression):
        self.expression = expr
        self.state = HolderState.UNEVALUATED

    def link_visual(self, expr: VisualExpression):
        self.expression = expr
        return expr

    def evaluate(self):
        self.state = HolderState.EVALUATING
        announce("Evaluating", self, Root.root)

    def apply(self):
        self.state = HolderState.APPLYING
        announce("Applying", self, Root.root)

    def complete(self):
        self.state = HolderState.EVALUATED
        announce("Completed", self, Root.root)

    def __repr__(self):
        return repr(self.expression)


class Root:
    root: Holder

    @classmethod
    def setroot(cls, root: Holder):
        cls.root = root


def silence(*args): pass


def print_announce(message, local, root):
    print(f"{message:10}: {repr(local):50} {repr(root):20}")


class Logger:
    def __init__(self):
        self.states = []
        self.environments = {}
        self._out = []

    def reset(self):
        self.states = []
        self._out.append("")
        self.environments = {}

    def clear_out(self):
        self._out = []

    def log(self, message, local, root):
        # print_announce(message, local, root)
        new_state = freeze_state(root)
        # print(new_state.export())
        # print("\n" * 2)
        self.states.append(new_state)

    def export(self):
        return {"states": [state.export() for state in self.states], "out": [x.strip() for x in self._out]}

    def out(self, val):
        self._out[-1] += repr(val) + "\n"


print_delta = 0


class StateTree:
    def __init__(self, expr: Union[Expression, VisualExpression], transition_type: HolderState):
        self.transition_type = transition_type
        self.children = []
        if isinstance(expr, VisualExpression) and expr.value is None:
            for child in expr.children:
                self.children.append(StateTree(child.expression, child.state))

        if isinstance(expr, VisualExpression):
            self.base_str = repr(expr.base_expr)
            # self.id = expr.id
        else:
            self.base_str = repr(expr)
        self.str = repr(expr)

    def __repr__(self):
        return self.transition_type.name + " " + self.str + " " + repr(self.children)

    def export(self):
        return {
            "transition_type": self.transition_type.name,
            "str": self.str,
            # "id": self.id,
            "parent_str": self.base_str,
            "children": [x.export() for x in self.children]
        }


def freeze_state(state: Holder) -> StateTree:
    return StateTree(state.expression, state.state)


logger = Logger()
announce = logger.log
