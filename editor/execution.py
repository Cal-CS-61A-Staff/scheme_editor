from __future__ import annotations

from datamodel import Undefined
from evaluate_apply import evaluate
from gui import Holder, Root
from parser import get_expression
from lexer import TokenBuffer
from runtime_limiter import TimeLimitException
from scheme_exceptions import SchemeError


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

    import gui

    if global_frame is None:
        from environment import build_global_frame
        gui.logger.f_delta -= 1
        global_frame = build_global_frame()
        gui.logger.active_frames.pop(0)  # clear builtin frame
        gui.logger.f_delta += 1

    gui.logger.export_states = []
    gui.logger.roots = []

    gui.logger._out = []
    for i, string in enumerate(strings):
        if not string.strip():
            continue
        buff = TokenBuffer([string])
        while not buff.done:
            gui.logger.new_expr()
            expr = get_expression(buff)
            holder = Holder(expr, None)
            Root.setroot(holder)
            try:
                res = evaluate(expr, global_frame, holder)
                if res is not Undefined:
                    out(res)
            except (SchemeError, ZeroDivisionError, Exception) as e:
                if not gui.logger.fragile:
                    gui.logger.raw_out("Traceback (most recent call last)\n")
                    for i, expr in enumerate(gui.logger.eval_stack):
                        gui.logger.raw_out(str(i).ljust(3) + " " + expr + "\n")
                gui.logger.out(e)
            except TimeLimitException:
                if not gui.logger.fragile:
                    gui.logger.out("Time limit exceeded.")
        gui.logger.new_expr()