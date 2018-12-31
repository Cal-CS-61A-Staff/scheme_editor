(define (reverse lst)
  (cond 
   ((null? lst)
     nil)
   (else
     (append (reverse (cdr lst))
             (list (car lst))))))

(define (tail-reverse lst)
  (define (helper lst curr)
    (if (null? lst)
        curr
        (helper (cdr lst)
                (cons (car lst) curr))))
  (helper lst '()))

(let )

(cond 
 (#t
   5))