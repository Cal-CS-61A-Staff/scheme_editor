(define (count x total)
  (if (= x 0)
      total
      (count (- x 1)
             (+ x total))))