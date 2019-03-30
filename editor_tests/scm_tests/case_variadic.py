from scheme_runner import SchemeTestCase, Query, out

cases = [
    SchemeTestCase(
        [
            Query(code=['(define (f (variadic x)) (cons 10 x))'], expected=out("f")),
            Query(code="f", expected=out("(f (variadic x)) [parent = Global]")),
            Query(code=['(f 2 3)'], expected=out("(10 2 3)")),
            Query(code=['(variadic x)'], expected=out("Error")),
            Query(code=['(variadic 2)'], expected=out("Error")),
            Query(code=['(define (f . x) (cons 10 x))'], expected=out("f")),
            Query(code=['(f 2 3)'], expected=out("(10 2 3)")),
            Query(code=['. x'], expected=out("Error")),
            Query(code=['\' . x'], expected=out("(variadic x)")),
            Query(code=["'(1 . x)"], expected=out("(1 (variadic x))")),
        ])]
