from scheme_runner import SchemeTestCase, Query

cases = [
    SchemeTestCase([
        Query(code=['(define (f y) (set! x y))'], expected={'out': ['f\n']}),
        Query(code=['(define x 5)'], expected={'out': ['x\n']}),
        Query(code=['x'], expected={'out': ['5\n']}),
        Query(code=['(f 6)'], expected={'out': ['']}),
        Query(code=['x'], expected={'out': ['6\n']})
    ]),
    SchemeTestCase([
        Query(code=['(define x 5)'], expected={'out': ['x\n']}),
        Query(code=['(define (f x y) (print x) (set! x y) x)'], expected={'out': ['f\n']}),
        Query(code=['x'], expected={'out': ['5\n']}),
        Query(code=['(f 4 6)'], expected={'out': ['4\n6\n']}),
        Query(code=['x'], expected={'out': ['5\n']})
    ]),
]
