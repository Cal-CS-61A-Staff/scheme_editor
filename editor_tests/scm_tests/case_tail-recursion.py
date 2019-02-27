from scheme_runner import SchemeTestCase, Query
cases = [
SchemeTestCase([Query(code=['(define (sum n total)', '(if (zero? n) total', '(sum (- n 1) (+ n total))))'], expected={}), Query(code=['(sum 1001 0)'], expected={'out': ['501501\n']}), Query(code=['(define (sum n total)', '(cond ((zero? n) total)', '(else (sum (- n 1) (+ n total)))))'], expected={}), Query(code=['(sum 1001 0)'], expected={'out': ['501501\n']}), Query(code=['(define (sum n total)', '(begin 2 3', '(if (zero? n) total', '(and 2 3', '(or false', '(begin 2 3', '(let ((m n))', '(sum (- m 1) (+ m total)))))))))'], expected={}), Query(code=['(sum 1001 0)'], expected={'out': ['501501\n']})])
]
