from scheme_runner import SchemeTestCase, Query
cases = [
SchemeTestCase([Query(code=['(expect 1 2)'], expected={'out': ['Evaluated 1, expected 2, got 1.\n']}), Query(code=['(expect (+ 1 1) 2)'], expected={'out': ['Evaluated (+ 1 1), got 2, as expected.\n']}), Query(code=['(expect (+ 1 1) (+ 1 1))'], expected={'out': ['Evaluated (+ 1 1), expected (+ 1 1), got 2.\n']})])
]
