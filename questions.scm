(define (reverse lst)
  (cond ((null? lst) nil)
        (else (append (reverse (cdr lst))
                      (car lst)))))