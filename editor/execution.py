from __future__ import annotations

from datamodel import Undefined
from evaluate_apply import evaluate
from log import Holder, Root
from parser import get_expression
from lexer import TokenBuffer
from runtime_limiter import TimeLimitException
from scheme_exceptions import SchemeError


def string_exec(strings, out, global_frame=None):
    """"
    >>> log.silent = True

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
    """

    import log

    if global_frame is None:
        from environment import build_global_frame
        log.logger.f_delta -= 1
        global_frame = build_global_frame()
        log.logger.active_frames.pop(0)  # clear builtin frame
        log.logger.f_delta += 1

    log.logger.export_states = []
    log.logger.roots = []
    log.logger.frame_updates = []
    log.logger._out = []

    for i, string in enumerate(strings):
        if not string.strip():
            continue
        buff = TokenBuffer([string])
        while not buff.done:
            expr = get_expression(buff)
            print(expr)
            if expr is None:
                continue
            log.logger.new_expr()
            holder = Holder(expr, None)
            Root.setroot(holder)
            try:
                res = evaluate(expr, global_frame, holder)
                if res is not Undefined:
                    out(res)
            except (SchemeError, ZeroDivisionError, RecursionError, ValueError) as e:
                if not log.logger.fragile:
                    log.logger.raw_out("Traceback (most recent call last)\n")
                    for i, expr in enumerate(log.logger.eval_stack):
                        log.logger.raw_out(str(i).ljust(3) + " " + expr + "\n")
                log.logger.out(e)
                break
            except TimeLimitException:
                if not log.logger.fragile:
                    log.logger.out("Time limit exceeded.")
                break
        log.logger.new_expr()
