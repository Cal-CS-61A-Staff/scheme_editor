from src.datamodel import Expression, Boolean, Number, Symbol, Nil, SingletonTrue, SingletonFalse, Pair, bools
from src.environment import global_attr
from src.helper import pair_to_list
from src.primitives import SingleOperandPrimitive
from src.scheme_exceptions import OperandDeduceError
from src.special_forms import LambdaObject, MuObject


@global_attr("atom?")
class IsAtom(SingleOperandPrimitive):
    def execute_simple(self, operand: Expression):
        return bools[isinstance(operand, Boolean) or isinstance(operand, Number)
                     or isinstance(operand, Symbol) or operand is Nil]


@global_attr("boolean?")
class IsBoolean(SingleOperandPrimitive):
    def execute_simple(self, operand: Expression):
        return bools[isinstance(operand, Boolean)]


@global_attr("integer?")
class IsInteger(SingleOperandPrimitive):
    def execute_simple(self, operand: Expression):
        return bools[isinstance(operand, Number)]


@global_attr("list?")
class IsList(SingleOperandPrimitive):
    def execute_simple(self, operand: Expression):
        if isinstance(operand, Pair):
            try:
                pair_to_list(operand)
                return SingletonTrue
            except OperandDeduceError:
                return SingletonFalse
        else:
            return SingletonFalse


@global_attr("number?")
class IsNumber(SingleOperandPrimitive):
    def execute_simple(self, operand: Expression) -> Expression:
        return bools[isinstance(operand, Number)]


@global_attr("null?")
class IsNull(SingleOperandPrimitive):
    def execute_simple(self, operand: Expression) -> Expression:
        if operand is Nil:
            return SingletonTrue
        else:
            return SingletonFalse


@global_attr("pair?")
class IsPair(SingleOperandPrimitive):
    def execute_simple(self, operand: Expression) -> Expression:
        return bools[isinstance(operand, Pair)]


@global_attr("procedure?")
class IsProcedure(SingleOperandPrimitive):
    def execute_simple(self, operand: Expression):
        return bools[isinstance(operand, LambdaObject) or isinstance(operand, MuObject)]


@global_attr("string?")
class IsString(SingleOperandPrimitive):
    def execute_simple(self, operand: Expression) -> Expression:
        raise NotImplementedError("Strings are not (yet) supported!")


@global_attr("symbol?")
class IsSymbol(SingleOperandPrimitive):
    def execute_simple(self, operand: Expression) -> Expression:
        return bools[isinstance(operand, Symbol)]
