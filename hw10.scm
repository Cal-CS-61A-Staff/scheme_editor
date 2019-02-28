(define (loop n)
  (if (zero? n) (/ 1 0) (loop (- n 1))))

(loop 300)