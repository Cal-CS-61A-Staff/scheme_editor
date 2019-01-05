(define (accumulate combiner start n term)
  (if (= n 0)
      start
      (combiner (term n)
                (accumulate combiner
                            start
                            (- n 1)
                            term))))

(define (accumulate-tail combiner start n term)
  (if (= n 0)
      start
      (accumulate-tail combiner
                       (combiner start (term n))
                       (- n 1)
                       term)))

(define (partial-sutms stream)
  (define (helper k stream)
    (if (null? stream)
        nil
        (cons-stream (+ k (car stream))
                     (helper (+ k (car stream))
                             (cdr-stream stream)))))
  (helper 0 stream))

(define (rle s)
  (cond
   ((null? s)
    nil)
   (else
    (define (helper cnt s)
      (if (null? (cdr-stream s))
          (cons cnt nil)
          (if (eq? (car s)
                   (car (cdr-stream s)))
              (helper (+ 1 cnt) (cdr-stream s))
              (cons cnt (cdr-stream s)))))
    (define ret (helper 1 s))
    (cons-stream
     (list (car s) (car ret))
     (rle (cdr ret))))))