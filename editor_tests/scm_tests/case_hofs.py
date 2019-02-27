from scheme_runner import SchemeTestCase, Query
cases = [
SchemeTestCase([Query(code=['(define (cube x) (* x x x))'], expected={}), Query(code=['(define (sum term a next b)', '(if (> a b)', '0', '(+ (term a)', '(sum term (next a) next b))))'], expected={}), Query(code=['(define (inc n) (+ n 1))'], expected={}), Query(code=['(define (sum-cubes a b)', '(sum cube a inc b))'], expected={}), Query(code=['(sum-cubes 1 10)'], expected={'out': ['3025\n']}), Query(code=['(define (identity x) x)'], expected={}), Query(code=['(define (sum-integers a b)', '(sum identity a inc b))'], expected={}), Query(code=['(sum-integers 1 10)'], expected={'out': ['55\n']})])
]
