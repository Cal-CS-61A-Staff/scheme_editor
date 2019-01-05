(define a (cons-stream 1 (delay 2)))

(define b (cdr a))

(print (cdr-stream a))

(define a 5)