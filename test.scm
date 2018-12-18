(define (range start end curr)
  (if (= start end)
      curr
      (range (+ 1 start)
             end
             (cons start curr))))