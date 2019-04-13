(begin 1 2 3 (+ 5 6) 4)

(define (f x)
  (if (= x 0)
      nil
      (f (- x 1))))

(f 5)

(define (reverse curr lst)
  (if (null? lst)
      curr
      (reverse (cons (car lst) curr) (cdr lst))))

(define (reverse lst)
  (if (null? lst)
      nil
      (append (reverse (cdr lst)) (list (car lst)))))
