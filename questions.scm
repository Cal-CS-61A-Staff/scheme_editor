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
 (#t 5))

(+ (* 2 3) (/ 17 5))

(+ 1 (foo 3.5 a) bar baz)

(list (foo) (bar) (baz))

(let ((pi 3.14)
      (r 120))
  (* pi r r))

(define (factorial n)
  (if (zero? n)
      1 ; ONE
      (* n (factorial (- n 1)))))

(cond
 ((good? x) (handle-good x))
 ((bad? x)  (handle-bad x))
 ((ugly? x) (handle-ugly x))
 (else      (handle-default x)))