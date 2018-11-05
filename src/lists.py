from typing import List

from src.datamodel import Expression, Pair, Nil, Number
from src.environment import global_attr
from src.evaluate_apply import Frame
from src.helper import pair_to_list, make_list, verify_exact_callable_length
from src.primitives import SingleOperandPrimitive, BuiltIn
from src.scheme_exceptions import OperandDeduceError


@global_attr("append")
class Append(BuiltIn):
    def execute_evaluated(self, operands: List[Expression], frame: Frame) -> Expression:
        if len(operands) == 0: return Nil
        out = []
        for operand in operands[:-1]:
            if not isinstance(operand, Pair) and operand is not Nil:
                raise OperandDeduceError(f"Expected operand to be valid list, not {operand}")
            out.extend(pair_to_list(operand))
        try:
            last = operands[-1]
            if not isinstance(last, Pair):
                raise OperandDeduceError()
            last = pair_to_list(last)
        except OperandDeduceError:
            return make_list(out, operands[-1])
        else:
            out.extend(last)
            return make_list(out)


@global_attr("car")
class Car(SingleOperandPrimitive):
    def execute_simple(self, operand: Expression) -> Expression:
        if isinstance(operand, Pair):
            return operand.first
        else:
            raise OperandDeduceError(f"Unable to extract first element, as {operand} is not a Pair.")


@global_attr("cdr")
class Cdr(SingleOperandPrimitive):
    def execute_simple(self, operand: Expression) -> Expression:
        if isinstance(operand, Pair):
            return operand.rest
        else:
            raise OperandDeduceError(f"Unable to extract second element, as {operand} is not a Pair.")


@global_attr("cons")
class Cons(BuiltIn):
    def execute_evaluated(self, operands: List[Expression], frame: Frame) -> Expression:
        verify_exact_callable_length(self, 2, len(operands))
        return Pair(operands[0], operands[1])


@global_attr("length")
class Length(SingleOperandPrimitive):
    def execute_simple(self, operand: Expression) -> Expression:
        if not isinstance(operand, Pair) and operand is not Nil:
            raise OperandDeduceError(f"Unable to calculate length, as {operand} is not a valid list.")
        return Number(len(pair_to_list(operand)))


# @global_attr("map")
# class Map(BuiltIn):
#     def execute_evaluated(self, operands: List[Expression], frame: Frame) -> Expression:
#         verify_exact_callable_length(self, 2, len(operands))
#
#         func, lst = operands
#
#         if not isinstance(func, Callable):
#             raise OperandDeduceError(f"Unable to call {operands[0]}.")
#
#         if not isinstance(lst, Pair):
#             raise OperandDeduceError(f"Unable to iterate, since {operands[1]} is not a valid list.")
#
#         lst = pair_to_list(lst)
#         out = [func.execute([x], frame, dummy_holder) for x in lst]
#
#         return make_list(out)


@global_attr("list")
class List(BuiltIn):
    def execute_evaluated(self, operands: List[Expression], frame: Frame) -> Expression:
        return make_list(operands)
