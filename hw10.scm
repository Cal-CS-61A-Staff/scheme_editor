(define (accumulate op start num term)
  (if (= num 0)
      start
      (accumulate op
                       (op (term num) start)
                       (- num 1)
                       term)))
                   
(define accumulate-tail accumulate)

(define (partial-sums stream)
  (define (helper stream offset)
    (if
     (null? stream)
     nil
     (cons-stream (+ (car stream) offset)
                  (helper (cdr-stream stream)
                          (+ (car stream) offset)))))
  (helper stream 0))

(define (rle stream)
  (define (helper val stream)
    (cond
     ((null? stream)
      (list 0 stream))
     ((= (car stream) val)
      (define rest (helper val (cdr-stream stream)))
      (list (+ 1 (car rest)) (car (cdr rest))))
     (else
      (list 0 stream))))
  (cond
   ((null? stream)
    nil)
   (else
    (define ret (helper (car stream) stream))
    (define rest (rle (car (cdr ret))))
    (cons-stream (list (car stream) (car ret)) rest))))
