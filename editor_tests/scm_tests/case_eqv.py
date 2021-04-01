from scheme_runner import SchemeTestCase, Query
cases = [
SchemeTestCase([Query(code=['(eq? 1.0 1.0)'], expected={'out': ['#f\n']}), Query(code=['(eqv? 1.0 1.0)'], expected={'out': ['#t\n']})])
]
