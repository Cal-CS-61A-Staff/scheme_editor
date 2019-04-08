(f a ; a
   b ; x
   c)

cat

dog

(1 2 3 4 5 6)

(cond ((= 1 2)    3) ;comment
      ;second comment
      ((= 4456 5) 6) ; third comment
)

(cond (; comment
       (let 1
            2
            4) ; comment
      ) ; comment
      (c
       d) ; comment
)

(let ((pi 3.14)
      (r 120)) ; comment
  (* pi r r) ; comment
)

(let ((+ (cond (; comment
                (+ 1 2 4) ; comment
               ) ; comment
               (c
                d) ; comment
         ))
      (r 120)) ; comment
  (* pi r r) ; comment
)

(let ((pi (cond ((+ 1 2 4) 6)
                (c         d)))
      (r 120))
  (* pi r r))

(define (falalalalalalalalalalalalalalafalalalalalalalalalalalalalala x)
  (+ 1 x))

(define (f a b . c) (+ a b c))

((if 1
     2
     3)
 4)

(f ; comment
   a
   b)
