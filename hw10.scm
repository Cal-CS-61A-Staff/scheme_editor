(define (factorial x)
  (define (helper x curr)
    (if (= x 1)
        curr
        (helper (- fx 1)
                (* x curr))))
  (helper x 1))

(define (accumulate-tail op start num term)
  (if (= num 0)
      start
      (accumulate-tail op
                       (op start (term num))
                       (- num 1)
                       term)))

(define (partial-sums stream)
  (define (helper curr s)
    (if (null? s)
        nil
        (cons-stream (+ curr (car s))
                     (helper (+ curr (car s))
                             (cdr-stream s)))))
  (helper 0 stream))