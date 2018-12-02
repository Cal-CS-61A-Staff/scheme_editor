(define (factorial n)
    (if (= n 1) 1
        (let ((ans (factorial (- n 1))))
            (* n ans))))
    
(factorial 2)