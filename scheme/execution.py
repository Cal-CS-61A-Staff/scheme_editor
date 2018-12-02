from __future__ import annotations

from scheme.datamodel import Undefined
from scheme.evaluate_apply import evaluate
from scheme.gui import Holder, Root
from scheme.parser import get_expression
from scheme.lexer import TokenBuffer


def string_exec(strings, out, global_frame=None):
    """
    >>> gui.silent = True

    >>> string_exec(["(define cat 1)", "(+ cat 2)"])
    cat
    3
    >>> string_exec(["(define f (lambda x (+ x 1) (+ x 2) ))", "(f 2)"])
    f
    4
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
    >>> string_exec(["(* (+ 1 2) 4 5)"])
    60
    >>> string_exec(["(= (+ 1 3) (* 2 2))"])
    #t
    >>> string_exec(["(begin (define (f b) (if (= b 0) 0 (+ 1 (f (- b 1))))) (f 3))"])
    3
    """''

    from scheme import gui

    if global_frame is None:
        from scheme.environment import build_global_frame
        global_frame = build_global_frame()

    gui.logger._out = []
    for i, string in enumerate(strings):
        if not string.strip():
            continue
        buff = TokenBuffer([string])
        while not buff.done:
            gui.logger.clear_diagram()
            expr = get_expression(buff)
            holder = Holder(expr, None)
            Root.setroot(holder)
            res = evaluate(expr, global_frame, holder)
            if res is not Undefined:
                out(res)
