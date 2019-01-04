+ ; expect #[+]

display ; expect #[display]

hello ; expect SchemeError

2 ; expect 2

2 ; expect 2

2 ; expect 2

2 ; expect 2

2 ; expect 2

2 ; expect 2

(+ 2 2) ; expect 4

; expect 12 
(+ (+ 2 2) (+ 1 3) (* 1 4))

(yolo) ; expect SchemeError

(+ 2 3) ; expect 5

(* (+ 3 2) (+ 1 7)) ; expect 40

(1 2) ; expect SchemeError

(1 (print 0)) ; expect SchemeError

(+) ; expect 0

(odd? 13) ; expect #t

(car (list 1 2 3 4)) ; expect 1

(car car) ; expect SchemeError

(odd? 1 2 3) ; expect SchemeError

; expect 25 
(+ (+ 1)
   (* 2 3)
   (+ 5)
   (+ 6 (+ 7)))

(*) ; expect 1

(-) ; expect SchemeError

; expect 3 
(car (cdr (cdr (list 1 2 3 4))))

; expect SchemeError 
(car cdr (list 1))

; expect 6 
(* (car (cdr (cdr (list 1 2 3 4))))
   (car (cdr (list 1 2 3 4))))

; expect SchemeError 
(* (car (cdr (cdr (list 1 2 3 4))))
   (cdr (cdr (list 1 2 3 4))))

(+ (/ 1 0)) ; expect SchemeError

((/ 1 0) (print 5)) ; expect SchemeError

(null? (print 5)) ; expect #f

(define size 2) ; expect size

size ; expect 2

(define x (+ 2 3)) ; expect x

x ; expect 5

(define x (+ 2 7)) ; expect x

x ; expect 9

; expect 6.28 
(eval (define tau 6.28))

(define pi 3.14159) ; expect pi

(define radius 10) ; expect radius

; expect area 
(define area
  (* pi (* radius radius)))

area ; expect 314.159

(define radius 100) ; expect radius

radius ; expect 100

area ; expect 314.159

(define 0 1) ; expect SchemeError

(define error (/ 1 0)) ; expect SchemeError

(quote hello) ; expect hello

(quote hello) ; expect hello

(quote (1 2)) ; expect (1 2)

(quote (1 2)) ; expect (1 2)

(quote (1 . 2)) ; expect (1 . 2)

(quote (1 2)) ; expect (1 2)

(car (quote (1 2 3))) ; expect 1

(cdr (quote (1 2))) ; expect (2)

(car (car (quote ((1))))) ; expect 1

(quote 3) ; expect 3

; expect 4 
(eval
 (cons (quote car) (quote ((quote (4 2))))))

(quasiquote (1 2 3)) ; expect (1 2 3)

(define a 2) ; expect a

(quasiquote (unquote a)) ; expect 2

; expect (a b c) 
(quasiquote (a b c))

; expect (2 b c) 
(quasiquote ((unquote a) b c))

; expect SchemeError 
(quasiquote
 ((unquote a) (unquote b) c))

; expect SchemeError 
(quasiquote ((unquote
              (+ (unquote a) (unquote a)))
             b))

; expect (quasiquote (1 2 (+ 3 4))) 
(quasiquote (quasiquote (1 2 (+ 3 4))))

; expect (1 (2 b 3)) 
(quasiquote
 (1 (unquote
     (cons a
           (quasiquote (b (unquote (+ 1 2))))))))

(begin (+ 2 3) (+ 5 6)) ; expect 11

(begin (define x 3) x) ; expect 3

; expect (+ 2 2) 
(begin 30 (quote (+ 2 2)))

(define x 0) ; expect x

; expect x 
(begin 42 (define x (+ x 1)))

x ; expect 1

; expect hello 
(begin 30 (quote hello))

; expect (3 y z) 
(begin (define x 3)
       (cons x (quote (y z))))

; expect (3 x z) 
(begin (define x 3)
       (cons x (quote (x z))))

(define x 0) ; expect x

; expect x 
(begin (define x (+ x 1))
       (define x (+ x 10))
       (define x (+ x 100))
       (define x (+ x 1000)))

x ; expect 1111

; expect (lambda (x y) (+ x y)) 
(lambda (x y) (+ x y))

; expect (lambda (x) (+ x) (+ x x)) 
(lambda
 (x)
 (+ x)
 (+ x x))

(lambda (x)) ; expect SchemeError

(lambda nil 2) ; expect (lambda () 2)

(define (f) (+ 2 2)) ; expect f

f ; expect (lambda () (+ 2 2))

; expect f 
(define (f x) (* x x))

f ; expect (lambda (x) (* x x))

(define (foo x) 1 2 3 4 5) ; expect foo

foo ; expect (lambda (x) 1 2 3 4 5)

(define (foo) (/ 1 0)) ; expect foo

foo ; expect (lambda () (/ 1 0))

; expect square 
(define (square x) (* x x))

square ; expect (lambda (x) (* x x))

(square 21) ; expect 441

square ; expect (lambda (x) (* x x))

; expect square 
(define square (lambda (x) (* x x)))

(square (square 21)) ; expect 194481

; expect ((lambda (x) (list x (list (quote quote) x))) (quote (lambda (x) (list x (list (quote quote) x))))) 
((lambda (x)
         (list x
               (list (quote quote) x)))
 (quote (lambda (x)
                (list x
                      (list (quote quote) x)))))

; expect outer 
(define (outer x y)
  (define (inner z x)
    (+ x
       (* y 2)
       (* z 3)))
  (inner x 10))

(outer 1 2) ; expect 17

; expect outer-func 
(define (outer-func x y)
  (define (inner z x)
    (+ x
       (* y 2)
       (* z 3)))
  inner)

((outer-func 1 2) 1 10) ; expect 17

; expect square 
(define square (lambda (x) (* x x)))

; expect sum-of-squares 
(define (sum-of-squares x y)
  (+ (square x) (square y)))

(sum-of-squares 3 4) ; expect 25

; expect double 
(define double (lambda (x) (* 2 x)))

; expect compose 
(define compose
  (lambda (f g)
          (lambda (x) (f (g x)))))

; expect apply-twice 
(define apply-twice (lambda (f) (compose f f)))

((apply-twice double) 5) ; expect 20

(and) ; expect #t

(and 1 #f) ; expect #f

(and (+ 1 1) 1) ; expect 1

(and #f 5) ; expect #f

(and 4 5 (+ 3 3)) ; expect 6

; expect #f 
(and #t #f 42 (/ 1 0))

; expect #t 
(not (and #f))

(and 3 2 #f) ; expect #f

(and 3 2 1) ; expect 1

(and 3 #f 5) ; expect #f

(and 0 1 2 3) ; expect 3

(define (true-fn) #t) ; expect true-fn

(and (true-fn)) ; expect #t

(define x #f) ; expect x

; expect #f 
(and x #t)

(define x 0) ; expect x

; expect x 
(and (define x (+ x 1))
     (define x (+ x 10))
     (define x (+ x 100))
     (define x (+ x 1000)))

x ; expect 1111

(define x 0) ; expect x

; expect #f 
(and (define x (+ x 1))
     (define x (+ x 10))
     #f
     (define x (+ x 100))
     (define x (+ x 1000)))

x ; expect 11

; expect no-mutation 
(define (no-mutation)
  (and #t #t #t #t))

no-mutation ; expect (lambda () (and #t #t #t #t))

(no-mutation) ; expect #t

no-mutation ; expect (lambda () (and #t #t #t #t))

(or) ; expect #f

(or (+ 1 1)) ; expect 2

; expect #t 
(not (or #f))

(define (t) #t) ; expect t

(or (t) 3) ; expect #t

(or 5 2 1) ; expect 5

(or #f (- 1 1) 1) ; expect 0

(or 4 #t (/ 1 0)) ; expect 4

(or 0 1 2) ; expect 0

; expect a 
(or (quote a) #f)

; expect #t 
(or (< 2 3) (> 2 3) 2 (quote a))

(or (< 2 3) 2) ; expect #t

(define (false-fn) #f) ; expect false-fn

; expect yay 
(or (false-fn) (quote yay))

(define x 0) ; expect x

; expect #f 
(or
 (begin (define x (+ x 1)) #f)
 (begin (define x (+ x 10)) #f)
 (begin (define x (+ x 100)) #f)
 (begin (define x (+ x 1000)) #f))

x ; expect 1111

(define x 0) ; expect x

; expect #t 
(or
 (begin (define x (+ x 1)) #f)
 (begin (define x (+ x 10)) #f)
 #t
 (begin (define x (+ x 100)) #f)
 (begin (define x (+ x 1000)) #f))

x ; expect 11

; expect no-mutation 
(define (no-mutation)
  (or #f #f #f #f))

no-mutation ; expect (lambda () (or #f #f #f #f))

(no-mutation) ; expect #f

no-mutation ; expect (lambda () (or #f #f #f #f))

; expect greater-than-5 
(define (greater-than-5 x)
  (if (> x 5) #t #f))

; expect other 
(define (other y)
  (or (greater-than-5 y) #f))

(other 2) ; expect #f

(other 6) ; expect #t

; expect other 
(define (other y)
  (and (greater-than-5 y) #t))

(other 2) ; expect #f

(other 6) ; expect #t

; expect 7 
(cond
 ((> 2 3) 5)
 ((> 2 4) 6)
 ((< 2 5) 7)
 (else    8))

; expect 8 
(cond
 ((> 2 3) 5)
 ((> 2 4) 6)
 (else    8))

(if 0 1 2) ; expect 1

(if #f 1 (if #t 2 3)) ; expect 2

; expect a 
(if (= 1 2) (/ 1 0) (quote a))

; expect 7 
(cond
 ((> 2 3) 5)
 ((> 2 4) 6)
 ((< 2 5) 7))

(cond
 ((> 2 3)
  (display (quote oops))
  (newline))
 (else
  9))

(cond
 ((< 2 1)
  )
 ((> 3 2)
  )
 (else
  5))

; expect  
(cond
 (#f 1))

; expect hi 
(cond
 ((= 4 3) (quote nope))
 ((= 4 4) (quote hi))
 (else    (quote wat)))

(cond
 ((= 4 3)
  (quote wat))
 ((= 4 4)
  )
 (else
  (quote hm)))

(cond
 ((= 4 4)
  (+ 40 2))
 (else
  (quote wat)
  0))

; expect 12 
(cond
 (12
  ))

; expect hi 
(cond
 ((= 4 3)
  )
 ((quote hi)
  ))

; expect  
(eval (cond
       (#f 1)
       (#f 2)))

; expect yea 
(cond
 (0    (quote yea))
 (else (quote nay)))

(define x 0) ; expect x

(define y 0) ; expect y

(define z 0) ; expect z

(cond
 (#t
  (define x (+ x 1))
  (define y (+ y 1))
  (define z (+ z 1)))
 (else
  (define x (- x 5))
  (define y (- y 5))
  (define z (- z 5))))

; expect (1 1 1) 
(list x y z)

; expect print-and-false 
(define (print-and-false val) (print val) #f)

; expect  
(cond
 ((print-and-false (quote cond1))
  )
 ((print-and-false (quote cond2))
  )
 ((print-and-false (quote cond3))
  )
 ((print-and-false (quote cond4))
  ))

; expect print-and-true 
(define (print-and-true val) (print val) #t)

; expect #t 
(cond
 ((print-and-false (quote cond1))
  )
 ((print-and-false (quote cond2))
  )
 ((print-and-true (quote cond3))
  )
 ((print-and-false (quote cond4))
  ))

(define x 1) ; expect x

; expect 8 
(let ((x 5))
  (+ x 3))

x ; expect 1

; expect SchemeError 
(let ((a 1)
      (b a))
  b)

; expect 9 
(let ((x 5))
  (let ((x 2)
        (y x))
    (+ y (* x 2))))

; expect square 
(define (square x) (* x x))

; expect f 
(define (f x y)
  (let ((a (+ 1 (* x y)))
        (b (- 1 y)))
    (+ (* x (square a))
       (* y b)
       (* a b))))

(f 3 4) ; expect 456

(define x 3) ; expect x

(define y 4) ; expect y

; expect (6 . 5) 
(let ((x (+ y 2))
      (y (+ x 2)))
  (cons x y))

; expect hello 
(let ((x (quote hello)))
  x)

; expect 6 
(let ((a 1)
      (b 2)
      (c 3))
  (+ a b c))

(define z 0) ; expect z

; expect 1 
(let ((a (define z (+ z 1))))
  z)

; expect (2 . 3) 
(let ((x 1)
      (y 3))
  (define x (+ x 1))
  (cons x y))

; expect SchemeError 
(let ((a 1 1))
     a)

; expect SchemeError 
(let ((a 1)
      (2 2))
  a)

(define y 1) ; expect y

; expect f 
(define f (mu (x) (+ x y)))

; expect g 
(define g
  (lambda (x y)
          (f (+ x x))))

(g 3 7) ; expect 13

; expect h 
(define h (mu nil x))

; expect high 
(define (high fn x) (fn))

(high h 2) ; expect 2

; expect f 
(define (f x)
  (mu nil (lambda (y) (+ x y))))

; expect g 
(define (g x)
  (((f (+ x 1))) (+ x 2)))

(g 3) ; expect 8

(mu nil) ; expect SchemeError

; expect None 
(load (quote questions))

; expect ((0 3) (1 4) (2 5) (3 6)) 
(enumerate (quote (3 4 5 6)))

; expect ((0 9) (1 8) (2 7) (3 6) (4 5) (5 4)) 
(enumerate (quote (9 8 7 6 5 4)))

; expect None 
(load (quote questions))

; expect ((0 a) (1 b) (2 c) (3 d)) 
(enumerate
 (quote (a b c d)))

(enumerate (quote nil)) ; expect ()

; expect None 
(load (quote questions))

; expect ((10) (5 5) (5 1 1 1 1 1) (1 1 1 1 1 1 1 1 1 1)) 
(list-change 10 (quote (25 10 5 1)))

; expect ((4 1) (3 2) (3 1 1) (2 2 1) (2 1 1 1) (1 1 1 1 1)) 
(list-change 5 (quote (4 3 2 1)))

; expect None 
(load (quote questions))

; expect ((5 2) (5 1 1) (4 3) (4 2 1) (4 1 1 1) (3 3 1) (3 2 2) (3 2 1 1) (3 1 1 1 1) (2 2 2 1) (2 2 1 1 1) (2 1 1 1 1 1) (1 1 1 1 1 1 1)) 
(list-change 7 (quote (5 4 3 2 1)))

; expect None 
(load (quote questions))

(let-to-lambda 1) ; expect 1

; expect a 
(let-to-lambda (quote a))

; expect (+ 1 2) 
(let-to-lambda (quote (+ 1 2)))

; expect ((lambda (a b) (+ a b)) 1 2) 
(let-to-lambda
 (quote (let ((a 1)
              (b 2))
          (+ a b))))

; expect None 
(load (quote questions))

; expect (quoted expressions remain the same) 
(quote
 (quoted expressions remain the same))

; expect (quote (let ((a 1) (b 2)) (+ a b))) 
(let-to-lambda
 (quote (quote (let ((a 1)
                     (b 2))
                 (+ a b)))))

; expect None 
(load (quote questions))

; expect (lambda parameters not affected but body affected) 
(quote
 (lambda parameters
         not
         affected
         but
         body
         affected))

; expect (lambda (let a b) (+ let a b)) 
(let-to-lambda
 (quote (lambda (let a
                     b)
                (+ let
                   a
                   b))))

; expect (lambda (x) a ((lambda (a) a) x)) 
(let-to-lambda
 (quote (lambda (x)
                a
                (let ((a x))
                  a))))

; expect None 
(load (quote questions))

; expect ((lambda (a b) (+ a b)) ((lambda (a) a) 2) 2) 
(let-to-lambda
 (quote (let ((a (let ((a 2))
                   a))
              (b 2))
          (+ a b))))

; expect ((lambda (a) ((lambda (b) b) a)) 1) 
(let-to-lambda
 (quote (let ((a 1))
          (let ((b a))
            b))))

; expect (+ 1 ((lambda (a) a) 1)) 
(let-to-lambda (quote (+ 1
                         (let ((a 1))
                           a))))

; expect map 
(define (map f lst)
  (if (null? lst)
      nil
      (cons (f (car lst))
            (map f (cdr lst)))))

; expect for 
(define-macro (for formal iterable body)
  (list (quote map)
        (list (quote lambda) (list formal) body)
        iterable))

; expect (0 2 3) 
(for i
     (quote (1 2 3))
     (if (= i 1) 0 i))

; expect map 
(define (map f lst)
  (if (null? lst)
      nil
      (cons (f (car lst))
            (map f (cdr lst)))))

; expect cadr 
(define (cadr s) (car (cdr s)))

; expect cars 
(define (cars s) (map car s))

; expect cadrs 
(define (cadrs s) (map cadr s))

; expect leet 
(define-macro (leet bindings expr)
  (cons
   (list (quote lambda) (cars bindings) expr)
   (cadrs bindings)))

; expect square 
(define (square x) (* x x))

; expect hyp 
(define (hyp a b)
  (leet ((a2 (square a))
         (b2 (square b)))
        (sqrt (+ a2 b2))))

(hyp 3 4) ; expect 5.0

; expect map 
(define (map f lst)
  (if (null? lst)
      nil
      (cons (f (car lst))
            (map f (cdr lst)))))

(define-macro wat?) ; expect SchemeError

(define-macro woah okay) ; expect SchemeError

(define-macro (hello world)) ; expect SchemeError

(define-macro (5) (cons 1 2)) ; expect SchemeError

(define-macro (name) (body)) ; expect name

name ; expect (lambda () (body))

(name) ; expect SchemeError

(quote (1 2 3 4 5 . 6)) ; expect (1 2 3 4 5 . 6)

(quote (1 2)) ; expect (1 2)

(quote (1 . 2)) ; expect (1 . 2)

+ ; expect #[+]

cat ; expect SchemeError

floor ; expect #[floor]

(print "cat") ; expect

(display "cat") ; expect

(newline) ; expect

nil ; expect ()

(quote nil) ; expect ()

begin ; expect SchemeError

(sqrt 9) ; expect 3.0

3 ; expect 3

(= 3 3) ; expect #t

(quote #f) ; expect #f

(quote #f) ; expect #f

; expect  
(if (quote #f)
    (print "err")
    (print "success"))

(= (sqrt 9) 3) ; expect #t

(= (sqrt 9) 3) ; expect #t

(/ 1 0) ; expect SchemeError

(cat dog) ; expect SchemeError

nil ; expect ()

(sqrt -1)

(* (+) (*)) ; expect 0

; expect 3 
(+ (*) (*) (*))

(/) ; expect SchemeError

(/ 2) ; expect 0.5

(odd? #f) ; expect SchemeError

(-) ; expect SchemeError

(floor 2.5) ; expect 2

(define cat dog) ; expect SchemeError

(define cat cat) ; expect SchemeError

; expect SchemeError 
(define a b c)

; expect a 
(define (a) b c)

(a) ; expect SchemeError

(define a) ; expect SchemeError

(define) ; expect SchemeError

define ; expect SchemeError

; expect scope 
(define (scope)
  (define define 5)
  (+ define define))

(scope) ; expect 10

; expect scope 
(define (scope)
  (define (unquote cat) 5)
  (unquote 6))

(scope) ; expect 5

(unquote cat) ; expect SchemeError

; expect cat 
(define cat (quote cat))

(eval cat) ; expect cat

; expect cat 
(eval (eval (eval cat)))

(eval eval) ; expect #[eval]

; expect id 
(define (id x) x)

(define dog 5) ; expect dog

; expect (quote dog) 
(apply id (quote ((quote dog))))

; expect dog 
(apply id (quote (dog)))

; expect (quote (dog)) 
(apply eval
       (quote ((quote (quote (dog))))))

; expect (dog) 
(apply eval
       (list (quote (quote (dog)))))

; expect (quote dog) 
(apply eval
       (quote ((quote (quote dog)))))

; expect 5 
(apply eval (quote (dog)))

; expect x 
(define (x a b c)
  (+ a b c))

(define y +) ; expect y

; expect #t 
(= (x 4 66 1) (y 4 66 1))

; expect #f 
(eq? x y)

(define z +) ; expect z

; expect #t 
(eq? y z)

; expect 9 
((begin (print "cat") +) 2 3 4)

; expect SchemeError 
((print "1") (print "2"))

(define x 1) ; expect x

; expect x 
(define x (+ 1 x))

x ; expect 2

(define 2 x) ; expect SchemeError

(define #t #f) ; expect SchemeError

(define cat 5) ; expect cat

cat ; expect 5

cat ; expect 5

(quote (car 5)) ; expect (car 5)

; expect (print "cat") 
(quote (print "cat"))

; expect (quote (print (quote cat))) 
(quote (quote (print (quote cat))))

; expect  
(eval (quote (print "cat")))

; expect SchemeError 
(eval (quote ((print "cat"))))

(quasiquote (+ 1 2 3 4)) ; expect (+ 1 2 3 4)

; expect (1 2 3 9) 
(quasiquote (1 2 3 (unquote (+ 4 5))))

; expect (1 2 3 . 9) 
(quasiquote (1 2 3 unquote (+ 4 5)))

; expect SchemeError 
(quasiquote (1 2 3 unquote + 4 5))

; expect (1 2 3 (quasiquote (4 5 (unquote (+ 6 7 8))))) 
(quasiquote
 (1 2 3 (quasiquote (4 5 (unquote (+ 6 7 8))))))

; expect (1 2 3 (quasiquote (4 5 unquote + 6 7 8))) 
(quasiquote
 (1 2 3 (quasiquote (4 5 unquote + 6 7 8))))

(begin) ; expect SchemeError

; expect 4 
((lambda (x) (* x x)) 2)

(define x 6) ; expect x

; expect 12 
((lambda (y)
         (print y)
         (* x y))
 2)

(define x 7) ; expect x

; expect 14 
((lambda (y)
         (print y)
         (* x y))
 2)

(lambda (y)) ; expect SchemeError

; expect f 
(define (f x)
  (+ a b c))

f ; expect (lambda (x) (+ a b c))

; expect f 
(define (f x)
  (define (g y) (+ x y))
  g)

g ; expect SchemeError

; expect (lambda (y) (+ x y)) 
(f 5)

(and) ; expect #t

(or) ; expect #f

(and 1 2 3) ; expect 3

(and 1 2 #f 4) ; expect #f

(or #f #f 5) ; expect 5

; expect #f 
(or #f #f)

; expect  
(and (print 5) (print 6) (print 7))

; expect  
(or (print 5) (print 6) (print 7))

; expect 11 
(cond
 ((+ 5 6)
  ))

; expect #t 
(cond
 (else
  ))

(cond
 (else
  5
  6
  7))

; expect SchemeError 
(cond
 ((else 5 6 7)
  ))

; expect  
(cond
 (#t   (print "5"))
 (#t   (print "6"))
 (else (print "7")))

; expect  
(cond
 (#f
  )
 ((print "5")
  )
 ((print "6")
  ))

; expect 6 
(let ((cat 1)
      (dog 2)
      (elephant 3))
  (+ cat dog elephant))

elephant ; expect SchemeError

(define cat 1) ; expect cat

; expect 3 
(let ((cat 2))
  (+ 1 cat))

cat ; expect 1

(define cat 1) ; expect cat

; expect 2 
(let ((cat 2)
      (dog (+ 1 cat)))
  dog)

; expect f 
(define f
  (mu (x)
      (print x)
      (if (> x 0)
          (begin y
                 (define y x)
                 (f (- x 1)))
          1)))

(define y 5) ; expect y

(f y) ; expect 1

; expect tailcall 
(define (tailcall x)
  (if (> x 0)
      (tailcall (- x 1))
      (print "wow")))

; (tailcall 10000)
; expect  
; expect dotwice 
(define-macro (dotwice expr)
  (list (quote begin) expr expr))

(dotwice (print 5)) ; expect

; expect alwaysprint5 
(define-macro (alwaysprint5 expr) (list print 5))

(alwaysprint5 (print (/ 1 0))) ; expect

10 ; expect 10

(+ 137 349) ; expect 486

(- 1000 334) ; expect 666

(* 5 99) ; expect 495

(/ 10 5) ; expect 2

(+ 2.7 10) ; expect 12.7

(+ 21 35 12 7) ; expect 75

(* 25 4 12) ; expect 1200

(+ (* 3 5) (- 10 6)) ; expect 19

; expect 57 
(+ (* 3 (+ (* 2 4) (+ 3 5)))
   (+ (- 10 7) 6))

; expect 57 
(+ (* 3 (+ (* 2 4) (+ 3 5)))
   (+ (- 10 7) 6))

(define size 2) ; expect size

size ; expect 2

(* 5 size) ; expect 10

(define pi 3.14159) ; expect pi

(define radius 10) ; expect radius

; expect 314.159 
(* pi (* radius radius))

; expect circumference 
(define circumference (* 2 pi radius))

circumference ; expect 62.8318

; expect square 
(define (square x) (* x x))

(square 21) ; expect 441

; expect square 
(define square (lambda (x) (* x x)))

(square 21) ; expect 441

(square (+ 2 5)) ; expect 49

(square (square 3)) ; expect 81

; expect sum-of-squares 
(define (sum-of-squares x y)
  (+ (square x) (square y)))

(sum-of-squares 3 4) ; expect 25

; expect f 
(define (f a)
  (sum-of-squares (+ a 1) (* a 2)))

(f 5) ; expect 136

; expect abs 
(define (abs x)
  (cond
   ((> x 0) x)
   ((= x 0) 0)
   ((< x 0) (- x))))

(abs -3) ; expect 3

(abs 0) ; expect 0

(abs 3) ; expect 3

; expect a-plus-abs-b 
(define (a-plus-abs-b a b)
  ((if (> b 0) + -)
   a
   b))

(a-plus-abs-b 3 -2) ; expect 5

; expect sqrt-iter 
(define (sqrt-iter guess x)
  (if (good-enough? guess x)
      guess
      (sqrt-iter (improve guess x) x)))

; expect improve 
(define (improve guess x)
  (average guess (/ x guess)))

; expect average 
(define (average x y)
  (/ (+ x y) 2))

; expect good-enough? 
(define (good-enough? guess x)
  (<
   (abs (- (square guess) x))
   0.001))

; expect sqrt 
(define (sqrt x) (sqrt-iter 1 x))

(sqrt 9) ; expect 3.00009155413138

(sqrt (+ 100 37)) ; expect 11.704699917758145

; expect 1.7739279023207892 
(sqrt (+ (sqrt 2) (sqrt 3)))

(square (sqrt 1000)) ; expect 1000.000369924366

; expect sqrt 
(define (sqrt x)
  (define (good-enough? guess)
    (<
     (abs (- (square guess) x))
     0.001))
  (define (improve guess)
    (average guess (/ x guess)))
  (define (sqrt-iter guess)
    (if (good-enough? guess)
        guess
        (sqrt-iter (improve guess))))
  (sqrt-iter 1))

(sqrt 9) ; expect 3.00009155413138

(sqrt (+ 100 37)) ; expect 11.704699917758145

; expect 1.7739279023207892 
(sqrt (+ (sqrt 2) (sqrt 3)))

(square (sqrt 1000)) ; expect 1000.000369924366

; expect cube 
(define (cube x)
  (* x x x))

; expect sum 
(define (sum term a next b)
  (if (> a b)
      0
      (+ (term a)
         (sum term
              (next a)
              next
              b))))

; expect inc 
(define (inc n) (+ n 1))

; expect sum-cubes 
(define (sum-cubes a b)
  (sum cube a inc b))

(sum-cubes 1 10) ; expect 3025

; expect identity 
(define (identity x) x)

; expect sum-integers 
(define (sum-integers a b)
  (sum identity a inc b))

(sum-integers 1 10) ; expect 55

; expect 12 
((lambda (x y z)
         (+ x y (square z)))
 1
 2
 3)

; expect f 
(define (f x y)
  (let ((a (+ 1 (* x y)))
        (b (- 1 y)))
    (+ (* x (square a))
       (* y b)
       (* a b))))

(f 3 4) ; expect 456

(define x 5) ; expect x

; expect 38 
(+ (let ((x 3))
     (+ x (* x 10)))
   x)

; expect 21 
(let ((x 3)
      (y (+ x 2)))
  (* x y))

; expect add-rat 
(define (add-rat x y)
  (make-rat (+
             (* (numer x) (denom y))
             (* (numer y) (denom x)))
            (* (denom x) (denom y))))

; expect sub-rat 
(define (sub-rat x y)
  (make-rat (-
             (* (numer x) (denom y))
             (* (numer y) (denom x)))
            (* (denom x) (denom y))))

; expect mul-rat 
(define (mul-rat x y)
  (make-rat
   (* (numer x) (numer y))
   (* (denom x) (denom y))))

; expect div-rat 
(define (div-rat x y)
  (make-rat
   (* (numer x) (denom y))
   (* (denom x) (numer y))))

; expect equal-rat? 
(define (equal-rat? x y)
  (=
   (* (numer x) (denom y))
   (* (numer y) (denom x))))

(define x (cons 1 2)) ; expect x

(car x) ; expect 1

(cdr x) ; expect 2

(define x (cons 1 2)) ; expect x

(define y (cons 3 4)) ; expect y

; expect z 
(define z (cons x y))

(car (car z)) ; expect 1

(car (cdr z)) ; expect 3

z ; expect ((1 . 2) 3 . 4)

; expect make-rat 
(define (make-rat n d)
  (cons n d))

; expect numer 
(define (numer x) (car x))

; expect denom 
(define (denom x) (cdr x))

; expect print-rat 
(define (print-rat x)
  (display (numer x))
  (display (quote /))
  (display (denom x))
  (newline))

(define one-half (make-rat 1 2)) ; expect one-half

(print-rat one-half) ; expect

; expect one-third 
(define one-third (make-rat 1 3))

; expect  
(print-rat (add-rat one-half one-third))

; expect  
(print-rat (mul-rat one-half one-third))

; expect  
(print-rat (add-rat one-third one-third))

; expect gcd 
(define (gcd a b)
  (if (= b 0)
      a
      (gcd b (remainder a b))))

; expect make-rat 
(define (make-rat n d)
  (let ((g (gcd n d)))
    (cons (/ n g)
          (/ d g))))

; expect  
(print-rat (add-rat one-third one-third))

; expect one-through-four 
(define one-through-four (list 1 2 3 4))

one-through-four ; expect (1 2 3 4)

(car one-through-four) ; expect 1

(cdr one-through-four) ; expect (2 3 4)

(car (cdr one-through-four)) ; expect 2

(cons 10 one-through-four) ; expect (10 1 2 3 4)

(cons 5 one-through-four) ; expect (5 1 2 3 4)

; expect map 
(define (map proc items)
  (if (null? items)
      nil
      (cons (proc (car items))
            (map proc (cdr items)))))

; expect (10 2.5 11.6 17) 
(map abs
     (list -10 2.5 -11.6 17))

; expect (1 4 9 16) 
(map (lambda (x) (* x x))
     (list 1 2 3 4))

; expect scale-list 
(define (scale-list items factor)
  (map (lambda (x) (* x factor))
       items))

; expect (10 20 30 40 50) 
(scale-list (list 1 2 3 4 5) 10)

; expect count-leaves 
(define (count-leaves x)
  (cond
   ((null? x)
    0)
   ((not (pair? x))
    1)
   (else
    (+ (count-leaves (car x))
       (count-leaves (cdr x))))))

; expect x 
(define x (cons (list 1 2) (list 3 4)))

(count-leaves x) ; expect 4

; expect 8 
(count-leaves (list x x))

; expect odd? 
(define (odd? x) (= 1 (remainder x 2)))

; expect filter 
(define (filter predicate sequence)
  (cond
   ((null? sequence)
    nil)
   ((predicate (car sequence))
    (cons (car sequence)
          (filter predicate (cdr sequence))))
   (else
    (filter predicate (cdr sequence)))))

(filter odd? (list 1 2 3 4 5)) ; expect (1 3 5)

; expect accumulate 
(define (accumulate op initial sequence)
  (if (null? sequence)
      initial
      (op (car sequence)
          (accumulate op initial (cdr sequence)))))

(accumulate + 0 (list 1 2 3 4 5)) ; expect 15

(accumulate * 1 (list 1 2 3 4 5)) ; expect 120

; expect (1 2 3 4 5) 
(accumulate cons nil (list 1 2 3 4 5))

; expect enumerate-interval 
(define (enumerate-interval low high)
  (if (> low high)
      nil
      (cons low
            (enumerate-interval (+ low 1) high))))

(enumerate-interval 2 7) ; expect (2 3 4 5 6 7)

; expect enumerate-tree 
(define (enumerate-tree tree)
  (cond
   ((null? tree)
    nil)
   ((not (pair? tree))
    (list tree))
   (else
    (append (enumerate-tree (car tree))
            (enumerate-tree (cdr tree))))))

; expect (1 2 3 4 5) 
(enumerate-tree (list 1 (list 2 (list 3 4)) 5))

(define a 1) ; expect a

(define b 2) ; expect b

(list a b) ; expect (1 2)

; expect (a b) 
(list (quote a) (quote b))

; expect (a 2) 
(list (quote a) b)

; expect a 
(car (quote (a b c)))

; expect (b c) 
(cdr (quote (a b c)))

; expect memq 
(define (memq item x)
  (cond
   ((null? x)             #f)
   ((equal? item (car x)) x)
   (else                  (memq item (cdr x)))))

; expect #f 
(memq (quote apple)
      (quote (pear banana prune)))

; expect (apple pear) 
(memq (quote apple)
      (quote (x (apple sauce)
                y
                apple
                pear)))

; expect my-equal? 
(define (my-equal? x y)
  (cond
   ((pair? x)
    (and (pair? y)
         (my-equal? (car x) (car y))
         (my-equal? (cdr x) (cdr y))))
   ((null? x)
    (null? y))
   (else
    (equal? x y))))

; expect #t 
(my-equal? (quote (1 2 (three)))
           (quote (1 2 (three))))

; expect #f 
(my-equal? (quote (1 2 (three)))
           (quote (1 2 three)))

; expect #f 
(my-equal? (quote (1 2 three))
           (quote (1 2 (three))))

; expect double 
(define double (lambda (x) (* 2 x)))

(double 5) ; expect 10

; expect compose 
(define compose
  (lambda (f g)
          (lambda (x) (f (g x)))))

((compose list double) 5) ; expect (10)

; expect apply-twice 
(define apply-twice (lambda (f) (compose f f)))

((apply-twice double) 5) ; expect 20

((apply-twice (apply-twice double)) 5) ; expect 80

; expect fact 
(define fact
  (lambda (n)
          (if (<= n 1)
              1
              (* n (fact (- n 1))))))

(fact 3) ; expect 6

; expect 30414093201713378043612608166064768844377641568960512000000000000 
(fact 50)

; expect combine 
(define (combine f)
  (lambda (x y)
          (if (null? x)
              nil
              (f
               (list (car x) (car y))
               ((combine f)
                (cdr x)
                (cdr y))))))

; expect zip 
(define zip (combine cons))

; expect ((1 5) (2 6) (3 7) (4 8)) 
(zip (list 1 2 3 4) (list 5 6 7 8))

; expect riff-shuffle 
(define riff-shuffle
  (lambda
   (deck)
   (begin
    (define take
      (lambda (n seq)
              (if (<= n 0)
                  (quote nil)
                  (cons (car seq)
                        (take (- n 1) (cdr seq))))))
    (define drop
      (lambda (n seq)
              (if (<= n 0)
                  seq
                  (drop (- n 1) (cdr seq)))))
    (define mid (lambda (seq) (/ (length seq) 2)))
    ((combine append)
     (take (mid deck) deck)
     (drop (mid deck) deck)))))

; expect (1 5 2 6 3 7 4 8) 
(riff-shuffle (list 1 2 3 4 5 6 7 8))

; expect (1 3 5 7 2 4 6 8) 
((apply-twice riff-shuffle)
 (list 1 2 3 4 5 6 7 8))

; expect (1 2 3 4 5 6 7 8) 
(riff-shuffle
 (riff-shuffle
  (riff-shuffle (list 1 2 3 4 5 6 7 8))))

(apply square (quote (2))) ; expect 4

(apply + (quote (1 2 3 4))) ; expect 10

; expect (1 2 3 4) 
(apply (if #f + append) (quote ((1 2) (3 4))))

(if 0 1 2) ; expect 1

(if (quote nil) 1 2) ; expect 1

; expect #t 
(or #f #t)

(or) ; expect #f

(and) ; expect #t

(or 1 2 3) ; expect 1

(and 1 2 3) ; expect 3

; expect #f 
(and #f (/ 1 0))

; expect SchemeError 
(and #t (/ 1 0))

(or 3 (/ 1 0)) ; expect 3

; expect SchemeError 
(or #f (/ 1 0))

; expect hello 
(or (quote hello) (quote world))

(if nil 1 2) ; expect 1

(if 0 1 2) ; expect 1

; expect 2 
(if (or #f #f #f) 1 2)

(define (loop) (loop)) ; expect loop

(cond
 (#f
  (loop))
 (12
  ))

; expect 2 
((lambda (x) (display x) (newline) x) 2)

; expect g 
(define g (mu nil x))

; expect high 
(define (high f x) (f))

(high g 2) ; expect 2

; expect print-and-square 
(define (print-and-square x)
  (print x)
  (square x))

(print-and-square 12) ; expect 144

(/ 1 0) ; expect SchemeError

; expect addx 
(define addx (mu (x) (+ x y)))

; expect add2xy 
(define add2xy
  (lambda (x y)
          (addx (+ x x))))

(add2xy 3 7) ; expect 13

; expect 7 
(let ((x 2))
  ((begin (define x (+ x 1)) +)
   3
   (begin (define x (+ x 1)) x)))

; expect len 
(define (len s)
  (if (eq? s (quote nil))
      0
      (+ 1 (len (cdr s)))))

(len (quote (1 2 3 4))) ; expect 4

; expect sum 
(define (sum n total)
  (if (zero? n)
      total
      (sum (- n 1)
           (+ n total))))

; (sum 1001 0)
; expect 501501 
; expect sum 
(define (sum n total)
  (cond
   ((zero? n)
    total)
   (else
    (sum (- n 1)
         (+ n total)))))

; (sum 1001 0)
; expect 501501 
; expect sum 
(define (sum n total)
  (begin
   2
   3
   (if (zero? n)
       total
       (and 2
            3
            (or #f
                (begin 2
                       3
                       (let ((m n))
                         (sum (- m 1)
                              (+ m total)))))))))

; (sum 1001 0)
; expect 501501 
; expect SchemeError 
(exit)

; expect map 
(define (map f lst)
  (if (null? lst)
      nil
      (cons (f (car lst))
            (map f (cdr lst)))))

; expect for 
(define-macro (for formal iterable body)
  (list (quote map)
        (list (quote lambda) (list formal) body)
        iterable))

; expect (0 2 3) 
(for i
     (quote (1 2 3))
     (if (= i 1) 0 i))

; expect cadr 
(define (cadr s) (car (cdr s)))

; expect cars 
(define (cars s) (map car s))

; expect cadrs 
(define (cadrs s) (map cadr s))

; expect leet 
(define-macro (leet bindings expr)
  (cons
   (list (quote lambda) (cars bindings) expr)
   (cadrs bindings)))

; expect square 
(define (square x) (* x x))

; expect hyp 
(define (hyp a b)
  (leet ((a2 (square a))
         (b2 (square b)))
        (sqrt (+ a2 b2))))

(hyp 3 4) ; expect 5.000023178253949

; expect sum 
(define (sum n total)
  (if (zero? n)
      total
      (sum (- n 1)
           (+ n total))))

; (sum 1001 0)
; expect 501501 
; expect sum 
(define (sum n total)
  (if (zero? n)
      total
      (if #f
          42
          (sum (- n 1)
               (+ n total)))))

; (sum 1001 0)
; expect 501501 
; expect sum 
(define (sum n total)
  (cond
   ((zero? n)
    total)
   ((zero? 0)
    (sum (- n 1)
         (+ n total)))
   (else
    42)))

; (sum 1001 0)
; expect 501501 
; expect sum 
(define (sum n total)
  (if (zero? n)
      total
      (add n (+ n total))))

; expect add 
(define add
  (lambda (x+1 y)
          (sum (- x+1 1) y)))

; (sum 1001 0)
; expect 501501 
; expect sum 
(define (sum n total)
  (if (zero? n)
      total
      (let ((n-1 (- n 1)))
        (sum n-1 (+ n total)))))

; (sum 1001 0)
; expect 501501 
; expect sum 
(define (sum n total)
  (or (and (zero? n) total)
      (add n (+ n total))))

; expect add 
(define add
  (lambda (x+1 y)
          (sum (- x+1 1) y)))

; (sum 1001 0)
; expect 501501 
; expect sum 
(define (sum n total)
  (define add
    (lambda (x+1 y)
            (sum (- x+1 1) y)))
  (or (and (zero? n) total)
      (add n (+ n total))))

; (sum 1001 0)
; expect 501501 
; expect sum 
; (sum 1001 0)
; expect 501501
(define (sum n total)
  (begin (define add
           (lambda (x+1 y)
                   (sum (- x+1 1) y)))
         (or (and (zero? n) total)
             (add n (+ n total)))))