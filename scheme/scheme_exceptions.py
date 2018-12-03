class SchemeError(Exception):
    def __repr__(self):
        return str(self)


class ParseError(SchemeError): pass


class SymbolLookupError(SchemeError): pass


class OperandDeduceError(SchemeError): pass


class CallableResolutionError(SchemeError): pass


class MathError(SchemeError): pass


class ComparisonError(SchemeError): pass


class TypeMismatchError(SchemeError): pass


class IrreversibleOperationError(SchemeError): pass
