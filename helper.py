from typing import List

from datamodel import Pair, Expression, Nil, Integer
from scheme_exceptions import OperandDeduceError, ArithmeticError, CallableResolutionError


def pair_to_list(pos: Pair) -> List[Expression]:
    out = []
    while pos is not Nil:
        if not isinstance(pos, Pair):
            raise OperandDeduceError(f"List terminated with '{operator}, not nil")
        out.append(pos.first)
        pos = pos.rest
    return out


def assert_all_integers(operands):
    for operand in operands:
        if not isinstance(operand, Integer):
            raise ArithmeticError(f"Unable to perform arithmetic, as {operand} is not an integer.")


def verify_exact_callable_length(operator: Expression, expected: int, actual: int):
    if expected != actual:
        raise CallableResolutionError(f"{operator} expected {expected} operands, received {actual}.")


def verify_min_callable_length(operator: Expression, expected: int, actual: int):
    if expected > actual:
        raise CallableResolutionError(f"{operator} expected {expected} operands, received {actual}.")