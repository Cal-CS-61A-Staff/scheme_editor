from scheme_runner import SchemeTestCase, Query
cases = [
SchemeTestCase([Query(code=['(define (square x) (* x x))'], expected={}), Query(code=["(map square '(1 2 3))"], expected={'out': ['(1 4 9)\n']}), Query(code=["(filter even? '(1 2 3 4 5))"], expected={'out': ['(2 4)\n']}), Query(code=["(reduce + '(1 2 3 4 5))"], expected={'out': ['15\n']}), Query(code=['(define (sum-of-squares x y)', '(+ (square x) (square y)))'], expected={}), Query(code=['(sum-of-squares 3 4)'], expected={'out': ['25\n']}), Query(code=['(define (f a)', '(sum-of-squares (+ a 1) (* a 2)))'], expected={}), Query(code=['(f 5)'], expected={'out': ['136\n']})])
]
