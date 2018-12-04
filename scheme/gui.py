from __future__ import annotations

from enum import Enum, auto
from typing import List, Union, Dict
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
        if isinstance(base_expr, ValueHolder) or isinstance(base_expr,evaluate_apply.Callable) \
                or base_expr == Nil or base_expr == Undefined:
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
        self.children = [Holder(expression, self) for expression in expressions]
        if expressions and isinstance(expressions[0], VisualExpression):
            logger.node_cache[self.id].modify(self, HolderState.EVALUATING)
        return self

    def __repr__(self):
        if self.value is not None:
            return repr(self.value)
        return repr(self.display_value)


class Holder:
    def __init__(self, expr: Expression, parent: VisualExpression):
        self.expression: Union[Expression, VisualExpression] = expr
        self.state = HolderState.UNEVALUATED
        self.parent = parent

    def link_visual(self, expr: VisualExpression):
        self.expression = expr
        if self.parent is not None:
            logger.node_cache[self.parent.id].modify(self.parent, HolderState.EVALUATING)
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
        self._out = [[]]
        self.i = 0
        self.start = 0
        self.node_cache = {}
        self.frame_lookup: Dict[int, StoredFrame] = {}
        self.active_frames: List[StoredFrame] = []
        self.strict_mode = False
        self.fragile = False

    def clear_diagram(self):
        self.node_cache = {}
        # self.i = 0
        self._out.append([])
        self.start = self.i

    def new_query(self):
        self.node_cache = {}
        self.i = 0
        self.start = 0
        self._out = []
        self.active_frames = []

    def preview_mode(self, val):
        self.fragile = val

    def log(self, message: str, local: Holder, root: Holder):
        self.new_node(local.expression, local.state)
        self.i += 1

    def export(self):
        states = {i.hex: v.export() for i, v in self.node_cache.items()}
        return {
            "root": Root.root.expression.id.hex,
            "states": states,
            "out": ["\n".join(["".join(x).strip() for x in self._out])],
            "environments": [f.export() for f in self.active_frames[1:]],
            "graphics": [],
            "start": self.start,
            "end": self.i,
            "globalFrameID": id(self.active_frames[1].base)
        }

    def out(self, val, end="\n"):
        self.raw_out(repr(val) + end)

    def raw_out(self, val):
        if self._out:
            self._out[-1].append(val)
        else:
            print(val, end="")

    def frame_create(self, frame: evaluate_apply.Frame):
        self.frame_lookup[id(frame)] = stored = StoredFrame(len(self.active_frames), frame)
        self.active_frames.append(stored)
        frame.id = stored.name

    def frame_store(self, frame: evaluate_apply.Frame, name: str, value: Expression):
        self.frame_lookup[id(frame)].bind(name, value)

    def new_node(self, expr: Union[Expression, VisualExpression], transition_type: HolderState):
        if isinstance(expr, Expression):
            key = uuid4()
            self.node_cache[key] = StaticNode(expr, transition_type)
            return key
        if expr.id in self.node_cache:
            return self.node_cache[expr.id].modify(expr, transition_type)
        node = FatNode(expr, transition_type)
        self.node_cache[node.id] = node
        return node.id


class StoredFrame:
    def __init__(self, i, base: evaluate_apply.Frame):
        if i == 0:
            name = "Builtins"
        elif i == 1:
            name = "Global"
        else:
            name = f"f{i}"
        self.name = name
        self.label = base.name
        self.parent = base.parent
        self.bindings = []
        self.base = base

    def bind(self, name: str, value: Expression):
        self.bindings.append((logger.i, (name, str(value))))

    def export(self):
        return {"name": self.name,
                "label": self.label,
                "parent": logger.frame_lookup[id(self.parent)].name,
                "bindings": self.bindings}


class StaticNode:
    def __init__(self, expr: Expression, transition_type: HolderState):
        self.expr = expr
        self.transition_type = transition_type

    def export(self):
        return {
            "transitions": [(0, self.transition_type.name)],
            "strs": [(0, repr(self.expr))],
            "parent_strs": [(0, repr(self.expr))],
            "children": [(0, [])],
            "static": True
        }


class FatNode:
    def __init__(self, expr: VisualExpression, transition_type: HolderState=HolderState.UNEVALUATED):
        self.transitions = []
        self.str = []
        self.base_str = []
        self.children = []
        self.id = expr.id
        self.modify(expr, transition_type)

    def modify(self, expr: Union[Expression, VisualExpression], transition_type: HolderState):
        if not self.transitions or self.transitions[-1][1] != transition_type.name:
            self.transitions.append((logger.i, transition_type.name))
        if not self.str or self.str[-1][1] != repr(expr):
            self.str.append((logger.i, repr(expr)))

        if self.children and self.children[-1][0] == logger.i:
            self.children.pop()

        if isinstance(expr, VisualExpression) and expr.value is None:
            self.children.append(
                (logger.i,
                 [logger.new_node(child.expression, child.state) for child in expr.children]))
        else:
            self.children.append((logger.i, []))

        if isinstance(expr, VisualExpression):
            new_base_str = repr(expr.base_expr)
        else:
            new_base_str = expr

        if not self.base_str or self.base_str[-1][1] != new_base_str:
            self.base_str.append((logger.i, new_base_str))

        return self.id

    def export(self):
        return {
            "transitions": self.transitions,
            "strs": self.str,
            "parent_strs": self.base_str,
            "children": [(i, [x.hex for x in y]) for i, y in self.children]
        }


return_symbol = Symbol("Return Value")

logger = Logger()
announce = logger.log
