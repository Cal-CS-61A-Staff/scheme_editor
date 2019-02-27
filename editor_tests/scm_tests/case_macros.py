from scheme_runner import SchemeTestCase, Query
cases = [
SchemeTestCase([Query(code=['(define x 7)'], expected={}), Query(code=["(define-macro (test) (define x 5) (list '+ 'x 4))"], expected={}), Query(code=['(test)'], expected={'out': ['11\n']}), Query(code=['(define-macro (when test . branch)', "(list 'if test (cons 'begin branch)))"], expected={}), Query(code=['(when true', '(define a 1)', '(define b 1)', '(+ a 1))'], expected={'out': ['2\n']}), Query(code=['a'], expected={'out': ['1\n']}), Query(code=['b'], expected={'out': ['1\n']}), Query(code=['(when false', '(define a 2)', '(define b 2))'], expected={}), Query(code=['a'], expected={'out': ['1\n']}), Query(code=['b'], expected={'out': ['1\n']})])
]
