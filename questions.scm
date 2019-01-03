(define (reverse lst)
  (cond
   ((null? lst)
    nil)
   (else
    (append (reverse (cdr lst))
            (list (car lst))))))

;;; bad
(define (tail-reverse lst)
  (define (helper lst curr)
    (if (null? lst)
        curr
        (helper (cdr lst)
                (cons (car lst) curr))))
  (helper lst '()))

(define (f x)
  (if (< (g x) 3)
      (h x 2)))

(define (prime? x)
  (if
   (<= x 1)
   #f
   (null? (filter (lambda (y) (= 0 (remainder x y))) (range 2 x)))))

(null? (filter (lambda (y) (= 0 (remainder x y))) (range 2 x)))