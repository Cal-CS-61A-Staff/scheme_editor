from datamodel import Undefined

import memory_usage
from evaluate_apply import evaluate
from log import Holder, Root
from execution_parser import get_expression
from lexer import TokenBuffer
from runtime_limiter import TimeLimitException
from scheme_exceptions import SchemeError


def string_exec(strings, out, global_frame=None):
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

    memory_usage.reset()

    for i, string in enumerate(strings):
        try:
            if not string.strip():
                continue
            buff = TokenBuffer([string])
            while not buff.done:
                expr = get_expression(buff)
                if expr is None:
                    continue
                log.logger.new_expr()
                holder = Holder(expr, None)
                Root.setroot(holder)
                res = evaluate(expr, global_frame, holder)
                if res is not Undefined:
                    out(res)
        except (SchemeError, ZeroDivisionError, RecursionError, ValueError) as e:
            if not log.logger.fragile:
                log.logger.raw_out("Traceback (most recent call last)\n")
                for j, expr in enumerate(log.logger.eval_stack):
                    log.logger.raw_out(str(j).ljust(3) + " " + expr + "\n")
            log.logger.out(e)
        except TimeLimitException:
            if not log.logger.fragile:
                log.logger.out("Time limit exceeded.")
        log.logger.new_expr()
