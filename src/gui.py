from __future__ import annotations

from enum import Enum, auto
from typing import List, Union
from uuid import uuid4

from src.datamodel import Expression, ValueHolder, Pair, Nil, Symbol
from src import evaluate_apply
from src.helper import pair_to_list
from src.scheme_exceptions import OperandDeduceError


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
            try:
                self.set_entries(pair_to_list(base_expr))
            except OperandDeduceError:
                self.set_entries([base_expr.first, base_expr.rest])
        else:
            raise NotImplementedError(base_expr)

    def set_entries(self, expressions: List[Expression]):
        self.value = None
        self.children = [Holder(expression) for expression in expressions]
        return self

    def __repr__(self):
        if self.value is not None:
            return str(self.value)
        return str(self.display_value)


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
        self.states = None
        self._out = None
        self.frames = None
        self.frame_lookup = None
        self.environments = None
        self.environment_indices = None
        self.skip_tree = None
        self.code = None
        self.hide_return_frames = False
        self.frame_cnt = None

        self.new_query(True, False)

    def clear_diagram(self):
        self.states = []
        self._out.append("")
        self.environment_indices = []
        self.environments = []
        self.frame_store(None, None, None)

    def new_query(self, skip_tree, hide_return_frames):
        self._out = []
        self.frames = []
        self.frame_lookup = {}
        self.clear_diagram()
        self._out = []
        self.skip_tree = skip_tree
        self.hide_return_frames = hide_return_frames
        self.frame_cnt = 0

    def log(self, message, local, root):
        if not self.skip_tree:
            new_state = freeze_state(root)
            self.states.append(new_state)
            # print("saving state")

    def export(self):
        return {"states": [state.export() for state in self.states],
                "out": [x.strip() for x in self._out],
                "environments": [*zip(self.environment_indices, self.environments)],
                "code": self.code,
                }

    def setID(self, code):
        self.code = code

    def out(self, val, end="\n"):
        self.raw_out(repr(val) + end)

    def raw_out(self, val, end="\n"):
        self._out[-1] += val

    def frame_create(self, frame):
        self.frame_lookup[frame] = len(self.frames)
        frame.id = self.frame_cnt
        self.frame_cnt += 1
        self.frames.append(frame)

    def frame_store(self, frame, name, value):
        if self.states and self.environment_indices and self.environment_indices[-1] == len(self.states) - 1:
            self.environments.pop()
            self.environment_indices.pop()
        self.environments.append([])
        for frame in self.frames:
            self.environments[-1].append(
                [[frame.id, frame.parent.id if frame.parent is not None else "Global", frame.name],
                 [[k, repr(v)] for k, v in frame.vars.items()]])
        self.environment_indices.append(len(self.states) - 1)
        if self.hide_return_frames:
            self.frames = [f for f in self.frames if return_symbol.value not in f.vars]
        if self.hide_return_frames and name is return_symbol.value:
            self.frame_store(frame, None, None)


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


return_symbol = Symbol("Return Value")

logger = Logger()
announce = logger.log
