(f a ; a
   b ; x
   c
)

cat

dog

(1 2 3 4 5 6)

(cond 
  ((= 1 2)    3) ; comment
  ; second comment
  ((= 4456 5) 6) ; third comment
)

(cond 
  (; comment
   (let 1
        2
        4
   ) ; comment
  ) ; comment
  (c
   d
  ) ; comment
)

(let ((pi 3.14)
      (r 120)
     ) ; comment
  (* pi r r) ; comment
)

(let ((+ (cond 
           (; comment
            (+ 1 2 4) ; comment
           ) ; comment
           (c
            d
           ) ; comment
         )
      )
      (r 120)
     ) ; comment
  (* pi r r) ; comment
)

(let ((pi (cond 
            ((+ 1 2 4) 6)
            (c         d)
          )
      )
      (r 120)
     )
  (* pi r r)
)

(define (catdog x) (+ 1 x))

(define (f a b . c) (+ a b c))

((if 1
     2
     3
 )
 4
)

(f ; comment
   a
   b
)

(define ; comment
        (f a b c) ; formals
  (+ a b c)
)

(cond 
  ((good? x)
   (handle-good x)
  )
  ((bad? x)
   (handle-bad (if (really-bad? x)
                   (really-bad->bad x)
                   x
               )
   )
  )
  ((ugly? x)
   (handle-ugly x)
  )
  (else
   (handle-default x)
  )
)

(+ 1 (foo 3.5 a) bar baz)
