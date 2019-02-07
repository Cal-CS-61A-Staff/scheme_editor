(define (sort lst)
  (if (null? lst)
      nil
      (let ((sortedRest (sort (cdr lst))))
        (define (insert val sortedRest)
          (cond
           ((null? sortedRest)
            (list val))
           ((> val (car sortedRest))
            (cons (car sortedRest)
                  (insert val (cdr sortedRest))))
           (else
            (cons val sortedRest))))
        (insert (car lst) sortedRest))))