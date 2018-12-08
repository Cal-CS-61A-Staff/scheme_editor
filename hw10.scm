(define (map2 func lst)
  (define (helper func curr lst)
    (if (null? lst)
        curr
        (helper func
                (cons (func (car lst)) curr)
                (cdr lst))))
  (helper (lambda (x) x)
          nil
          (helper func nil lst)))

(define (range start end curr)
  (if (= start end)
      curr
      (range (+ 1 start)
             end
             (cons start curr))))

(define (accumulate combiner start n term)
  (if (= n 0)
      start
      (combiner (term n)
                (accumulate combiner
                            start
                            (- n 1)
                            term))))

(define (accumulate-tail combiner start n term)
  (reduce combiner
          (cons start
                (map term (range 1 (+ 1 n) nil)))))

(define (partial-sums stream)
  (define (helper curr stream)
    (if (null? stream)
        nil
        (cons-stream (+ curr (car stream))
                     (helper (+ curr (car stream))
                             (cdr-stream stream)))))
  (helper 0 stream))

(define (rle s)
  (if (null? s)
      nil
      (begin (define (helper cnt s)
               (if (null? (cdr s))
                   (cons cnt nil)
                   (if (eq? (car s) (car (cdr s)))
                       (helper (+ 1 cnt) (cdr s))
                       (cons cnt (cdr s)))))
             (define ret (helper 1 s))
             (cons (list (car s) (car ret))
                   (rle (cdr ret))))))