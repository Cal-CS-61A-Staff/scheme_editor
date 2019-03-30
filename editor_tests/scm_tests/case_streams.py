from scheme_runner import SchemeTestCase, Query

cases = [
    SchemeTestCase([Query(code=['(define s (cons-stream 1 (cons-stream 2 nil)))'], expected={}),
                    Query(code=['(define t (cons-stream 1 (/ 1 0)))'], expected={}),
                    Query(
                        code=['(define (range-stream a b)',
                              '(if (>= a b) nil (cons-stream a (range-stream (+ a 1) b))))'],
                        expected={}),
                    Query(code=['(define (int-stream start)', '(cons-stream start (int-stream (+ start 1))))'],
                          expected={}),
                    Query(
                        code=['(define (prefix s k)', '(if (= k 0)', 'nil', '(cons (car s)', '(prefix (cdr-stream s)',
                              '(- k 1)))))'], expected={}),
                    Query(code=['(define ones (cons-stream 1 ones))'], expected={}),
                    Query(
                        code=['(define (square-stream s)', '(cons-stream (* (car s) (car s))',
                              '(square-stream (cdr-stream s))))'],
                        expected={}),
                    Query(
                        code=['(define (add-streams s t)', '(cons-stream (+ (car s) (car t))',
                              '(add-streams (cdr-stream s)',
                              '(cdr-stream t))))'], expected={}),
                    Query(code=['(define ints (cons-stream 1 (add-streams ones ints)))'], expected={}),
                    Query(code=['(define a (cons-stream 1 (cons-stream 2 (cons-stream 3 a))))'], expected={}),
                    Query(code=['(define (f s) (cons-stream (car s)', '(cons-stream (car s)', '(f (cdr-stream s)))))'],
                          expected={}),
                    Query(code=['(define (g s) (cons-stream (car s)', '(f (g (cdr-stream s)))))'], expected={}),
                    Query(
                        code=['(define (map-stream f s)', '(if (null? s)', 'nil', '(cons-stream (f (car s))',
                              '(map-stream f',
                              '(cdr-stream s)))))'], expected={}),
                    Query(
                        code=['(define (filter-stream f s)', '(if (null? s)', 'nil', '(if (f (car s))',
                              '(cons-stream (car s)',
                              '(filter-stream f (cdr-stream s)))', '(filter-stream f (cdr-stream s)))))'], expected={}),
                    Query(
                        code=['(define (reduce-stream f s start)', '(if (null? s)', 'start', '(reduce-stream f',
                              '(cdr-stream s)',
                              '(f start (car s)))))'], expected={}),
                    Query(code=['(define (sum-stream s)', '(reduce-stream + s 0))'], expected={}),
                    Query(
                        code=['(define (sum-primes-stream a b)',
                              '(sum-stream (filter-stream prime? (range-stream a b))))'],
                        expected={}),
                    Query(code=['(define (sieve s)', '(cons-stream', '(car s)', '(sieve (filter-stream',
                                '(lambda (x) (> (remainder x (car s)) 0))', '(cdr-stream s)))))'], expected={}),
                    Query(code=['(define primes (sieve (int-stream 2)))'], expected={}),
                    Query(code=['(prefix primes 10)'], expected={'out': ['(2 3 5 7 11 13 17 19 23 29)\n']})])
]
