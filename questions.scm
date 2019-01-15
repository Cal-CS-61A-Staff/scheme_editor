(define (reverse lst)
  (if (null? lst)
      nil
      (cons (reverse (cdr lst))
            (car lst))))

(define (iota n)
  (define (loop acc k)
    (if (= k n)
        (reverse acc)
        (loop (append (list k) acc)
              (+ 1 k))))
  (loop nil 0))

(iota 5)