from typing import List, Union, Tuple, Optional

from datamodel import Pair, Expression, Nil, Number, NilType
from scheme_exceptions import OperandDeduceError, MathError, CallableResolutionError


def pair_to_list(pos: Pair) -> List[Expression]:
    out = []
    while pos is not Nil:
        if not isinstance(pos, Pair):
            raise OperandDeduceError("List terminated with '{pos}', not nil".format(pos=pos))
        out.append(pos.first)
        pos = pos.rest
    return out


def dotted_pair_to_list(pos: Expression) -> Tuple[List[Expression], Optional[Expression]]:
    out = []
    vararg = None
    while pos is not Nil:
        if not isinstance(pos, Pair):
            vararg = pos
            break
        out.append(pos.first)
        pos = pos.rest
    return out, vararg


def assert_all_numbers(operands):
    for operand in operands:
        if not isinstance(operand, Number):
            raise MathError("Unable to perform arithmetic, as {operand} is not a number.".format(operand=operand))


def verify_exact_callable_length(operator: Expression, expected: int, actual: int):
    if expected != actual:
        raise CallableResolutionError("{operator} expected {expected} operands, received {actual}."
                                      .format(operator=operator, expected=expected, actual=actual))


def verify_min_callable_length(operator: Expression, expected: int, actual: int):
    if expected > actual:
        raise CallableResolutionError("{operator} expected at least {expected} operands, received {actual}."
                                      .format(operator=operator, expected=expected, actual=actual))


def make_list(exprs: List[Expression], last: Expression = Nil) -> Union[Pair, NilType]:
    if len(exprs) == 0:
        return last
    return Pair(exprs[0], make_list(exprs[1:], last))
