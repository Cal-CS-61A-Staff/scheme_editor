(define (loop x)
  (if (= x 0)
      5
      (loop (- x 1))))

(loop 1000)