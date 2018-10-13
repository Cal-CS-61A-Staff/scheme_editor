from typing import List

from datamodel import Pair, Expression, Nil
from scheme_exceptions import OperandDeduceError


def pair_to_list(pos: Pair) -> List[Expression]:
    out = []
    while pos is not Nil:
        if not isinstance(pos, Pair):
            raise OperandDeduceError(f"List terminated with '{operator}, not nil")
        out.append(pos.first)
        pos = pos.rest
    return out