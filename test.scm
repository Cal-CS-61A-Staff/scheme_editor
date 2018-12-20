(define (tailcall x)
  (if (> x 0)
      (tailcall (- x 1))
      (print "wow")))

(tailcall 100) ; expect tailcall
