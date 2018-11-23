(define (fact n)
    (if (= n 1)
        1
        (*
            (fact (- n 1))
            n)))
        
(fact 80)