(define (loop x)
  (if (= x 0)
      (/ 1 0)
      (loop (- x 1))))

(loop 2000)