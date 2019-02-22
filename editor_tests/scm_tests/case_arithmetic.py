from scheme_runner import SchemeTestCase, Query
cases = [
SchemeTestCase([Query(code=['10'], expected={'out': ['10\n']}), Query(code=['(+ 137 349)'], expected={'out': ['486\n']}), Query(code=['(- 1000 334)'], expected={'out': ['666\n']}), Query(code=['(* 5 99)'], expected={'out': ['495\n']}), Query(code=['(/ 10 5)'], expected={'out': ['2\n']}), Query(code=['(+ 2.7 10)'], expected={'out': ['12.7\n']}), Query(code=['(+ 21 35 12 7)'], expected={'out': ['75\n']}), Query(code=['(* 25 4 12)'], expected={'out': ['1200\n']}), Query(code=['(+ (* 3 5) (- 10 6))'], expected={'out': ['19\n']}), Query(code=['(+ (* 3 (+ (* 2 4) (+ 3 5))) (+ (- 10 7) 6))'], expected={'out': ['57\n']}), Query(code=['(+ (* 3', '(+ (* 2 4)', '(+ 3 5)))', '(+ (- 10 7)', '6))'], expected={'out': ['57\n']})])
]
