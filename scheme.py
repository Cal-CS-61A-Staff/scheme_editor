from __future__ import annotations

from evaluate_apply import evaluate
from parser import get_expression
from special_forms import build_global_frame
from lexer import TokenBuffer


def string_exec(strings):
    """
    >>> string_exec(["(define cat 1)", "(+ cat 2)"])
    cat
    3
    >>> string_exec(["(define f (lambda x (+ x 1)))", "(f 2)"])
    f
    3
    >>> string_exec(["(define f (lambda a (lambda b (+ a b))))", "(define add5 (f 5))", "(add5 2)"])
    f
    add5
    7
    >>> string_exec(["(define (f a b) (+ a b))", "(f 2 3)"])
    f
    5
    >>> string_exec(["(begin (define x 1) (define y (+ 1 x)))", "y"])
    y
    2
    >>> string_exec(["1"])
    1
    >>> string_exec(["(begin (if #f (define x 1) (define x 2)) x)"])
    2
    >>> string_exec(["(define x 5)", "x", "'x", "(quote x)", "(eval 'x)"])
    x
    5
    x
    x
    5
    """
    buff = TokenBuffer(strings)
    global_frame = build_global_frame()
    while not buff.done:
        print(evaluate(get_expression(buff), global_frame))


