from scheme_runner import SchemeTestCase, Query
cases = [
SchemeTestCase([Query(code=[], expected={}), Query(code=['(define (sqrt x)', '(define (good-enough? guess)', '(< (abs (- (square guess) x)) 0.001))', '(define (improve guess)', '(average guess (/ x guess)))', '(define (sqrt-iter guess)', '(if (good-enough? guess)', 'guess', '(sqrt-iter (improve guess))))', '(sqrt-iter 1.0))'], expected={}), Query(code=['(sqrt 9)'], expected={'out': ['3.00009155413138\n']}), Query(code=['(sqrt (+ 100 37))'], expected={'out': ['11.704699917758145\n']}), Query(code=['(sqrt (+ (sqrt 2) (sqrt 3)))'], expected={'out': ['1.7739279023207892\n']}), Query(code=['(square (sqrt 1000))'], expected={'out': ['1000.000369924366\n']})])
]
