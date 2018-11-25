(define (pop lst index)
    (define (helper left right index)
        (cond
            ((null? right) left)
            ((> index 0)
                (helper 
                    (append left (list (car right)))
                    (cdr right)
                    (- index 1)))
            (else
                (append left (cdr right)))))
    (helper nil lst index))

(pop nil 8)