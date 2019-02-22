from scheme_runner import SchemeTestCase, Query
cases = [
SchemeTestCase([Query(code=['(define (square x) (* x x))'], expected={}), Query(code=['((lambda (x y z) (+ x y (square z))) 1 2 3)'], expected={'out': ['12\n']}), Query(code=['(define (f x y)', '(let ((a (+ 1 (* x y)))', '(b (- 1 y)))', '(+ (* x (square a))', '(* y b)', '(* a b))))'], expected={}), Query(code=['(f 3 4)'], expected={'out': ['456\n']}), Query(code=['(define x 5)'], expected={}), Query(code=['(+ (let ((x 3))', '(+ x (* x 10)))', 'x)'], expected={'out': ['38\n']}), Query(code=['(let ((x 3)', '(y (+ x 2)))', '(* x y))'], expected={'out': ['21\n']})])
]
