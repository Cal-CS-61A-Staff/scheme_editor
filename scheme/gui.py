from __future__ import annotations

from enum import Enum, auto
from typing import List, Union
from uuid import uuid4

from scheme.datamodel import Expression, ValueHolder, Pair, Nil, Symbol, Undefined
from scheme import evaluate_apply
from scheme.helper import pair_to_list
from scheme.scheme_exceptions import OperandDeduceError


class HolderState(Enum):
    UNEVALUATED = auto()
    EVALUATING = auto()
    EVALUATED = auto()
    APPLYING = auto()


class VisualExpression:
    def __init__(self, base_expr: Expression = None, true_base_expr: Expression = None):
        self.display_value = base_expr
        self.base_expr = base_expr if true_base_expr is None else true_base_expr
        self.value: Expression = None
        self.children: List[Holder] = []
        self.id = uuid4()
        if base_expr is None:
            return
        if isinstance(base_expr, ValueHolder) or isinstance(base_expr,
                                                            evaluate_apply.Callable) or base_expr == Nil or base_expr == Undefined:
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
        self.strict_mode = None
        self.skip_envs = False

        self.new_query(True, True, False)

    def clear_diagram(self):
        self.states = []
        self._out.append([])
        self.environment_indices = []
        self.environments = []
        self.frame_store(None, None, None)

    def new_query(self, skip_tree, skip_envs, hide_return_frames, strict_mode=False):
        self.frames = []
        self.frame_lookup = {}
        self._out = []
        self.clear_diagram()
        self._out = []
        self.skip_tree = skip_tree
        self.skip_envs = skip_envs
        self.hide_return_frames = hide_return_frames
        self.frame_cnt = 0
        self.strict_mode = strict_mode

    def log(self, message, local, root):
        if not self.skip_tree:
            new_state = freeze_state(root)
            self.states.append(new_state)
            # print("saving state")

    def export(self):
        import scheme.graphics as graphics
        return {"states": [state.export() for state in self.states],
                "out": ["".join(x).strip() for x in self._out],
                "environments": [*zip(self.environment_indices, self.environments)],
                "code": self.code,
                "graphics": graphics.canvas.export(),
                }

    def setID(self, code):
        self.code = code

    def out(self, val, end="\n"):
        self.raw_out(repr(val) + end)

    def raw_out(self, val):
        if self._out:
            self._out[-1].append(val)
        else:
            print(val, end="")

    def frame_create(self, frame):
        self.frame_lookup[frame] = len(self.frames)
        frame.id = self.frame_cnt
        self.frame_cnt += 1
        self.frames.append(frame)

    def frame_store(self, frame, name, value):
        if self.skip_envs:
            return
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
        else:
            self.base_str = repr(expr)
        self.str = repr(expr)

    def __repr__(self):
        return self.transition_type.name + " " + self.str + " " + repr(self.children)

    def export(self):
        return {
            "transition_type": self.transition_type.name,
            "str": self.str,
            "parent_str": self.base_str,
            "children": [x.export() for x in self.children]
        }


def freeze_state(state: Holder) -> StateTree:
    return StateTree(state.expression, state.state)


return_symbol = Symbol("Return Value")

logger = Logger()
announce = logger.log