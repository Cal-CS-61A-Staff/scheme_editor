+

display ; expect #[+]

hello ; expect #[display]

2 ; expect SchemeError

2 ; expect 2

2 ; expect 2

2 ; expect 2

2 ; expect 2

2 ; expect 2

(+ 2 2) ; expect 2

(+ (+ 2 2) (+ 1 3) (* 1 4)) ; expect 4

(yolo) ; expect 12

(+ 2 3) ; expect SchemeError

(* (+ 3 2) (+ 1 7)) ; expect 5

(1 2) ; expect 40

(1 (print 0)) ; expect SchemeError

(+) ; expect SchemeError

(odd? 13) ; expect 0

(car (list 1 2 3 4)) ; expect #t

(car car) ; expect 1

(odd? 1 2 3) ; expect SchemeError

; expect SchemeError 
(+ (+ 1) (* 2 3) (+ 5) (+ 6 (+ 7)))

(*) ; expect 25

(-) ; expect 1

; expect SchemeError 
(car (cdr (cdr (list 1 2 3 4))))

(car cdr (list 1)) ; expect 3

; expect SchemeError 
(* (car (cdr (cdr (list 1 2 3 4))))
   (car (cdr (list 1 2 3 4))))

; expect 6 
(* (car (cdr (cdr (list 1 2 3 4))))
   (cdr (cdr (list 1 2 3 4))))

(+ (/ 1 0)) ; expect SchemeError

((/ 1 0) (print 5)) ; expect SchemeError

(null? (print 5)) ; expect SchemeError

(define size 2) ; expect #f

size ; expect size

(define x (+ 2 3)) ; expect 2

x ; expect x

(define x (+ 2 7)) ; expect 5

x ; expect x

(eval (define tau 6.28)) ; expect 9

(define pi 3.14159) ; expect 6.28

(define radius 10) ; expect pi

; expect radius 
(define area (* pi (* radius radius)))

area ; expect area

(define radius 100) ; expect 314.159

radius ; expect radius

area ; expect 100

(define 0 1) ; expect 314.159

; expect SchemeError 
(define error (/ 1 0))

(quote hello) ; expect SchemeError

(quote hello) ; expect hello

(quote (1 2)) ; expect hello

(quote (1 2)) ; expect (1 2)

(quote (1 . 2)) ; expect (1 2)

(quote (1 2)) ; expect (1 . 2)

(car (quote (1 2 3))) ; expect (1 2)

(cdr (quote (1 2))) ; expect 1

(car (car (quote ((1))))) ; expect (2)

(quote 3) ; expect 1

; expect 3 
(eval
 (cons (quote car)
       (quote ((quote (4 2))))))

(quasiquote (1 2 3)) ; expect 4

(define a 2) ; expect (1 2 3)

(quasiquote (unquote a)) ; expect a

(quasiquote (a b c)) ; expect 2

; expect (a b c) 
(quasiquote ((unquote a) b c))

; expect (2 b c) 
(quasiquote ((unquote a) (unquote b) c))

; expect SchemeError 
(quasiquote
 ((unquote (+ (unquote a) (unquote a)))
  b))

; expect SchemeError 
(quasiquote (quasiquote (1 2 (+ 3 4))))

; expect (quasiquote (1 2 (+ 3 4))) 
(quasiquote
 (1
  (unquote
   (cons a
         (quasiquote (b (unquote (+ 1 2))))))))

; expect (1 (2 b 3)) 
(begin (+ 2 3) (+ 5 6))

(begin (define x 3) x) ; expect 11

(begin 30 (quote (+ 2 2))) ; expect 3

(define x 0) ; expect (+ 2 2)

(begin 42 (define x (+ x 1))) ; expect x

x ; expect x

(begin 30 (quote hello)) ; expect 1

; expect hello 
(begin (define x 3)
       (cons x (quote (y z))))

; expect (3 y z) 
(begin (define x 3)
       (cons x (quote (x z))))

(define x 0) ; expect (3 x z)

; expect x 
(begin (define x (+ x 1))
       (define x (+ x 10))
       (define x (+ x 100))
       (define x (+ x 1000)))

x ; expect x

(lambda (x y) (+ x y)) ; expect 1111

; expect (lambda (x y) (+ x y)) 
(lambda (x) (+ x) (+ x x))

; expect (lambda (x) (+ x) (+ x x)) 
(lambda (x))

(lambda nil 2) ; expect SchemeError

; expect (lambda () 2) 
(define (f) (+ 2 2))

f ; expect f

; expect (lambda () (+ 2 2)) 
(define (f x) (* x x))

f ; expect f

; expect (lambda (x) (* x x)) 
(define (foo x) 1 2 3 4 5)

foo ; expect foo

; expect (lambda (x) 1 2 3 4 5) 
(define (foo) (/ 1 0))

foo ; expect foo

; expect (lambda () (/ 1 0)) 
(define (square x) (* x x))

square ; expect square

; expect (lambda (x) (* x x)) 
(square 21)

square ; expect 441

; expect (lambda (x) (* x x)) 
(define square (lambda (x) (* x x)))

(square (square 21)) ; expect square

; expect 194481 
((lambda (x)
         (list x (list (quote quote) x)))
 (quote
  (lambda (x)
          (list x (list (quote quote) x)))))

; expect ((lambda (x) (list x (list (quote quote) x))) (quote (lambda (x) (list x (list (quote quote) x))))) 
(define (outer x y)
  (define (inner z x)
    (+ x (* y 2) (* z 3)))
  (inner x 10))

(outer 1 2) ; expect outer

; expect 17 
(define (outer-func x y)
  (define (inner z x)
    (+ x (* y 2) (* z 3)))
  inner)

; expect outer-func 
((outer-func 1 2) 1 10)

; expect 17 
(define square (lambda (x) (* x x)))

; expect square 
(define (sum-of-squares x y)
  (+ (square x) (square y)))

; expect sum-of-squares 
(sum-of-squares 3 4)

; expect 25 
(define double (lambda (x) (* 2 x)))

; expect double 
(define compose
  (lambda (f g) (lambda (x) (f (g x)))))

; expect compose 
(define apply-twice
  (lambda (f) (compose f f)))

; expect apply-twice 
((apply-twice double) 5)

(and) ; expect 20

(and 1 #f) ; expect #t

(and (+ 1 1) 1) ; expect #f

(and #f 5) ; expect 1

(and 4 5 (+ 3 3)) ; expect #f

(and #t #f 42 (/ 1 0)) ; expect 6

(not (and #f)) ; expect #f

(and 3 2 #f) ; expect #t

(and 3 2 1) ; expect #f

(and 3 #f 5) ; expect 1

(and 0 1 2 3) ; expect #f

(define (true-fn) #t) ; expect 3

(and (true-fn)) ; expect true-fn

(define x #f) ; expect #t

(and x #t) ; expect x

(define x 0) ; expect #f

; expect x 
(and (define x (+ x 1))
     (define x (+ x 10))
     (define x (+ x 100))
     (define x (+ x 1000)))

x ; expect x

(define x 0) ; expect 1111

; expect x 
(and (define x (+ x 1))
     (define x (+ x 10))
     #f
     (define x (+ x 100))
     (define x (+ x 1000)))

x ; expect #f

; expect 11 
(define (no-mutation)
  (and #t #t #t #t))

no-mutation ; expect no-mutation

; expect (lambda () (and #t #t #t #t)) 
(no-mutation)

no-mutation ; expect #t

; expect (lambda () (and #t #t #t #t)) 
(or)

(or (+ 1 1)) ; expect #f

(not (or #f)) ; expect 2

(define (t) #t) ; expect #t

(or (t) 3) ; expect t

(or 5 2 1) ; expect #t

(or #f (- 1 1) 1) ; expect 5

(or 4 #t (/ 1 0)) ; expect 0

(or 0 1 2) ; expect 4

(or (quote a) #f) ; expect 0

; expect a 
(or (< 2 3) (> 2 3) 2 (quote a))

(or (< 2 3) 2) ; expect #t

(define (false-fn) #f) ; expect #t

; expect false-fn 
(or (false-fn) (quote yay))

(define x 0) ; expect yay

; expect x 
(or (begin (define x (+ x 1)) #f)
    (begin (define x (+ x 10)) #f)
    (begin (define x (+ x 100)) #f)
    (begin (define x (+ x 1000)) #f))

x ; expect #f

(define x 0) ; expect 1111

; expect x 
(or (begin (define x (+ x 1)) #f)
    (begin (define x (+ x 10)) #f)
    #t
    (begin (define x (+ x 100)) #f)
    (begin (define x (+ x 1000)) #f))

x ; expect #t

; expect 11 
(define (no-mutation) (or #f #f #f #f))

no-mutation ; expect no-mutation

; expect (lambda () (or #f #f #f #f)) 
(no-mutation)

no-mutation ; expect #f

; expect (lambda () (or #f #f #f #f)) 
(define (greater-than-5 x)
  (if (> x 5) #t #f))

; expect greater-than-5 
(define (other y)
  (or (greater-than-5 y) #f))

(other 2) ; expect other

(other 6) ; expect #f

; expect #t 
(define (other y)
  (and (greater-than-5 y) #t))

(other 2) ; expect other

(other 6) ; expect #f

; expect #t 
(cond ((> 2 3) 5)
      ((> 2 4) 6)
      ((< 2 5) 7)
      (else 8))

; expect 7 
(cond ((> 2 3) 5)
      ((> 2 4) 6)
      (else 8))

(if 0 1 2) ; expect 8

(if #f 1 (if #t 2 3)) ; expect 1

; expect 2 
(if (= 1 2) (/ 1 0) (quote a))

; expect a 
(cond ((> 2 3) 5)
      ((> 2 4) 6)
      ((< 2 5) 7))

; expect 7 
(cond
 ((> 2 3)
  (display (quote oops))
  (newline))
 (else 9))

; expect 9 
(cond ((< 2 1))
      ((> 3 2))
      (else 5))

; expect #t 
(cond (#f 1))

; expect  
(cond ((= 4 3) (quote nope))
      ((= 4 4) (quote hi))
      (else (quote wat)))

; expect hi 
(cond ((= 4 3) (quote wat))
      ((= 4 4))
      (else (quote hm)))

; expect #t 
(cond ((= 4 4) (+ 40 2))
      (else (quote wat) 0))

; expect 42 
(cond (12))

; expect 12 
(cond ((= 4 3))
      ((quote hi)))

; expect hi 
(eval (cond (#f 1)
            (#f 2)))

; expect  
(cond (0 (quote yea))
      (else (quote nay)))

(define x 0) ; expect yea

(define y 0) ; expect x

(define z 0) ; expect y

; expect z 
(cond
 (#t (define x (+ x 1))
     (define y (+ y 1))
     (define z (+ z 1)))
 (else (define x (- x 5))
       (define y (- y 5))
       (define z (- z 5))))

(list x y z) ; expect z

; expect (1 1 1) 
(define (print-and-false val)
  (print val)
  #f)

; expect print-and-false 
(cond ((print-and-false (quote cond1)))
      ((print-and-false (quote cond2)))
      ((print-and-false (quote cond3)))
      ((print-and-false (quote cond4))))

; expect  
(define (print-and-true val)
  (print val)
  #t)

; expect print-and-true 
(cond ((print-and-false (quote cond1)))
      ((print-and-false (quote cond2)))
      ((print-and-true (quote cond3)))
      ((print-and-false (quote cond4))))

(define x 1) ; expect #t

; expect x 
(let ((x 5))
  (+ x 3))

x ; expect 8

; expect 1 
(let ((a 1)
      (b a))
  b)

; expect SchemeError 
(let ((x 5))
  (let ((x 2)
        (y x))
    (+ y (* x 2))))

(define (square x) (* x x)) ; expect 9

; expect square 
(define (f x y)
  (let ((a (+ 1 (* x y)))
        (b (- 1 y)))
    (+ (* x (square a)) (* y b) (* a b))))

(f 3 4) ; expect f

(define x 3) ; expect 456

(define y 4) ; expect x

; expect y 
(let ((x (+ y 2))
      (y (+ x 2)))
  (cons x y))

; expect (6 . 5) 
(let ((x (quote hello)))
  x)

; expect hello 
(let ((a 1)
      (b 2)
      (c 3))
  (+ a b c))

(define z 0) ; expect 6

; expect z 
(let ((a (define z (+ z 1))))
  z)

; expect 1 
(let ((x 1)
      (y 3))
  (define x (+ x 1))
  (cons x y))

; expect (2 . 3) 
(let ((a 1 1))
     a)

; expect SchemeError 
(let ((a 1)
      (2 2))
  a)

(define y 1) ; expect SchemeError

(define f (mu (x) (+ x y))) ; expect y

; expect f 
(define g (lambda (x y) (f (+ x x))))

(g 3 7) ; expect g

(define h (mu nil x)) ; expect 13

(define (high fn x) (fn)) ; expect h

(high h 2) ; expect high

; expect 2 
(define (f x)
  (mu nil (lambda (y) (+ x y))))

; expect f 
(define (g x) (((f (+ x 1))) (+ x 2)))

(g 3) ; expect g

(mu nil) ; expect 8

; expect SchemeError 
(load (quote questions))

; expect None 
(enumerate (quote (3 4 5 6)))

; expect ((0 3) (1 4) (2 5) (3 6)) 
(enumerate (quote (9 8 7 6 5 4)))

; expect ((0 9) (1 8) (2 7) (3 6) (4 5) (5 4)) 
(load (quote questions))

; expect None 
(enumerate (quote (a b c d)))

; expect ((0 a) (1 b) (2 c) (3 d)) 
(enumerate (quote nil))

(load (quote questions)) ; expect ()

; expect None 
(list-change 10 (quote (25 10 5 1)))

; expect ((10) (5 5) (5 1 1 1 1 1) (1 1 1 1 1 1 1 1 1 1)) 
(list-change 5 (quote (4 3 2 1)))

; expect ((4 1) (3 2) (3 1 1) (2 2 1) (2 1 1 1) (1 1 1 1 1)) 
(load (quote questions))

; expect None 
(list-change 7 (quote (5 4 3 2 1)))

; expect ((5 2) (5 1 1) (4 3) (4 2 1) (4 1 1 1) (3 3 1) (3 2 2) (3 2 1 1) (3 1 1 1 1) (2 2 2 1) (2 2 1 1 1) (2 1 1 1 1 1) (1 1 1 1 1 1 1)) 
(load (quote questions))

(let-to-lambda 1) ; expect None

(let-to-lambda (quote a)) ; expect 1

; expect a 
(let-to-lambda (quote (+ 1 2)))

; expect (+ 1 2) 
(let-to-lambda
 (quote (let ((a 1) (b 2)) (+ a b))))

; expect ((lambda (a b) (+ a b)) 1 2) 
(load (quote questions))

; expect None 
(quote
 (quoted expressions remain the same))

; expect (quoted expressions remain the same) 
(let-to-lambda
 (quote
  (quote (let ((a 1) (b 2)) (+ a b)))))

; expect (quote (let ((a 1) (b 2)) (+ a b))) 
(load (quote questions))

; expect None 
(quote
 (lambda parameters
         not
         affected
         but
         body
         affected))

; expect (lambda parameters not affected but body affected) 
(let-to-lambda
 (quote (lambda (let a b) (+ let a b))))

; expect (lambda (let a b) (+ let a b)) 
(let-to-lambda
 (quote (lambda (x) a (let ((a x)) a))))

; expect (lambda (x) a ((lambda (a) a) x)) 
(load (quote questions))

; expect None 
(let-to-lambda
 (quote
  (let ((a (let ((a 2))
             a))
        (b 2))
    (+ a b))))

; expect ((lambda (a b) (+ a b)) ((lambda (a) a) 2) 2) 
(let-to-lambda
 (quote (let ((a 1)) (let ((b a)) b))))

; expect ((lambda (a) ((lambda (b) b) a)) 1) 
(let-to-lambda
 (quote (+ 1
           (let ((a 1))
             a))))

; expect (+ 1 ((lambda (a) a) 1)) 
(define (map f lst)
  (if (null? lst)
      nil
      (cons (f (car lst)) (map f (cdr lst)))))

; expect map 
(define-macro (for formal iterable body)
  (list (quote map)
        (list (quote lambda)
              (list formal)
              body)
        iterable))

; expect for 
(for i
     (quote (1 2 3))
     (if (= i 1) 0 i))

; expect (0 2 3) 
(define (map f lst)
  (if (null? lst)
      nil
      (cons (f (car lst)) (map f (cdr lst)))))

; expect map 
(define (cadr s) (car (cdr s)))

; expect cadr 
(define (cars s) (map car s))

; expect cars 
(define (cadrs s) (map cadr s))

; expect cadrs 
(define-macro (leet bindings expr)
  (cons
   (list (quote lambda)
         (cars bindings)
         expr)
   (cadrs bindings)))

; expect leet 
(define (square x) (* x x))

; expect square 
(define (hyp a b)
  (leet ((a2 (square a)) (b2 (square b)))
        (sqrt (+ a2 b2))))

(hyp 3 4) ; expect hyp

; expect 5.0 
(define (map f lst)
  (if (null? lst)
      nil
      (cons (f (car lst)) (map f (cdr lst)))))

(define-macro wat?) ; expect map

; expect SchemeError 
(define-macro woah okay)

; expect SchemeError 
(define-macro (hello world))

; expect SchemeError 
(define-macro (5) (cons 1 2))

; expect SchemeError 
(define-macro (name) (body))

name ; expect name

(name) ; expect (lambda () (body))

; expect SchemeError 
(quote (1 2 3 4 5 . 6))

(quote (1 2)) ; expect (1 2 3 4 5 . 6)

(quote (1 . 2)) ; expect (1 2)

+ ; expect (1 . 2)

cat ; expect #[+]

floor ; expect SchemeError

(print "cat") ; expect #[floor]

(display "cat") ; expect

(newline) ; expect

nil ; expect

(quote nil) ; expect ()

begin ; expect ()

(sqrt 9) ; expect SchemeError

3 ; expect 3.0

(= 3 3) ; expect 3

(quote #f) ; expect #t

(quote #f) ; expect #f

; expect #f 
(if (quote #f)
    (print "err")
    (print "success"))

(= (sqrt 9) 3) ; expect

(= (sqrt 9) 3) ; expect #t

(/ 1 0) ; expect #t

(cat dog) ; expect SchemeError

nil ; expect SchemeError

(sqrt -1) ; expect ()

(* (+) (*))

(+ (*) (*) (*)) ; expect 0

(/) ; expect 3

(/ 2) ; expect SchemeError

(odd? #f) ; expect 0.5

(-) ; expect SchemeError

(floor 2.5) ; expect SchemeError

(define cat dog) ; expect 2

(define cat cat) ; expect SchemeError

(define a b c) ; expect SchemeError

(define (a) b c) ; expect SchemeError

(a) ; expect a

(define a) ; expect SchemeError

(define) ; expect SchemeError

define ; expect SchemeError

; expect SchemeError 
(define (scope)
  (define define 5)
  (+ define define))

(scope) ; expect scope

; expect 10 
(define (scope)
  (define (unquote cat) 5)
  (unquote 6))

(scope) ; expect scope

(unquote cat) ; expect 5

; expect SchemeError 
(define cat (quote cat))

(eval cat) ; expect cat

(eval (eval (eval cat))) ; expect cat

(eval eval) ; expect cat

(define (id x) x) ; expect #[eval]

(define dog 5) ; expect id

; expect dog 
(apply id (quote ((quote dog))))

; expect (quote dog) 
(apply id (quote (dog)))

; expect dog 
(apply eval
       (quote ((quote (quote (dog))))))

; expect (quote (dog)) 
(apply eval
       (list (quote (quote (dog)))))

; expect (dog) 
(apply eval
       (quote ((quote (quote dog)))))

; expect (quote dog) 
(apply eval (quote (dog)))

(define (x a b c) (+ a b c)) ; expect 5

(define y +) ; expect x

(= (x 4 66 1) (y 4 66 1)) ; expect y

(eq? x y) ; expect #t

(define z +) ; expect #f

(eq? y z) ; expect z

; expect #t 
((begin (print "cat") +) 2 3 4)

((print "1") (print "2")) ; expect 9

(define x 1) ; expect SchemeError

(define x (+ 1 x)) ; expect x

x ; expect x

(define 2 x) ; expect 2

(define #t #f) ; expect SchemeError

(define cat 5) ; expect SchemeError

cat ; expect cat

cat ; expect 5

(quote (car 5)) ; expect 5

(quote (print "cat")) ; expect (car 5)

; expect (print "cat") 
(quote (quote (print (quote cat))))

; expect (quote (print (quote cat))) 
(eval (quote (print "cat")))

(eval (quote ((print "cat")))) ; expect

; expect SchemeError 
(quasiquote (+ 1 2 3 4))

; expect (+ 1 2 3 4) 
(quasiquote (1 2 3 (unquote (+ 4 5))))

; expect (1 2 3 9) 
(quasiquote (1 2 3 unquote (+ 4 5)))

; expect (1 2 3 . 9) 
(quasiquote (1 2 3 unquote + 4 5))

; expect SchemeError 
(quasiquote
 (1 2
    3
    (quasiquote (4 5 (unquote (+ 6 7 8))))))

; expect (1 2 3 (quasiquote (4 5 (unquote (+ 6 7 8))))) 
(quasiquote
 (1 2
    3
    (quasiquote (4 5 unquote + 6 7 8))))

; expect (1 2 3 (quasiquote (4 5 unquote + 6 7 8))) 
(begin)

; expect SchemeError 
((lambda (x) (* x x)) 2)

(define x 6) ; expect 4

; expect x 
((lambda (y) (print y) (* x y)) 2)

(define x 7) ; expect 12

; expect x 
((lambda (y) (print y) (* x y)) 2)

(lambda (y)) ; expect 14

; expect SchemeError 
(define (f x) (+ a b c))

f ; expect f

; expect (lambda (x) (+ a b c)) 
(define (f x) (define (g y) (+ x y)) g)

g ; expect f

(f 5) ; expect SchemeError

(and) ; expect (lambda (y) (+ x y))

(or) ; expect #t

(and 1 2 3) ; expect #f

(and 1 2 #f 4) ; expect 3

(or #f #f 5) ; expect #f

(or #f #f) ; expect 5

; expect #f 
(and (print 5) (print 6) (print 7))

; expect  
(or (print 5) (print 6) (print 7))

; expect  
(cond ((+ 5 6)))

; expect 11 
(cond (else))

; expect #t 
(cond (else 5 6 7))

; expect 7 
(cond ((else 5 6 7)))

; expect SchemeError 
(cond (#t (print "5"))
      (#t (print "6"))
      (else (print "7")))

; expect  
(cond (#f)
      ((print "5"))
      ((print "6")))

; expect  
(let ((cat 1)
      (dog 2)
      (elephant 3))
  (+ cat dog elephant))

elephant ; expect 6

(define cat 1) ; expect SchemeError

; expect cat 
(let ((cat 2))
  (+ 1 cat))

cat ; expect 3

(define cat 1) ; expect 1

; expect cat 
(let ((cat 2)
      (dog (+ 1 cat)))
  dog)

; expect 2 
(define f
  (mu (x)
      (print x)
      (if (> x 0)
          (begin y (define y x) (f (- x 1)))
          1)))

(define y 5) ; expect f

(f y) ; expect y

; expect 1 
(define (tailcall x)
  (if (> x 0)
      (tailcall (- x 1))
      (print "wow")))

; (tailcall 10000) ; expect tailcall

; expect  
(define-macro (dotwice expr)
  (list (quote begin) expr expr))

(dotwice (print 5)) ; expect dotwice

; expect  
(define-macro (alwaysprint5 expr)
  (list print 5))

; expect alwaysprint5 
(alwaysprint5 (print (/ 1 0)))

10 ; expect

(+ 137 349) ; expect 10

(- 1000 334) ; expect 486

(* 5 99) ; expect 666

(/ 10 5) ; expect 495

(+ 2.7 10) ; expect 2

(+ 21 35 12 7) ; expect 12.7

(* 25 4 12) ; expect 75

(+ (* 3 5) (- 10 6)) ; expect 1200

; expect 19 
(+ (* 3 (+ (* 2 4) (+ 3 5)))
   (+ (- 10 7) 6))

; expect 57 
(+ (* 3 (+ (* 2 4) (+ 3 5)))
   (+ (- 10 7) 6))

(define size 2) ; expect 57

size ; expect size

(* 5 size) ; expect 2

(define pi 3.14159) ; expect 10

(define radius 10) ; expect pi

(* pi (* radius radius)) ; expect radius

; expect 314.159 
(define circumference (* 2 pi radius))

circumference ; expect circumference

; expect 62.8318 
(define (square x) (* x x))

(square 21) ; expect square

; expect 441 
(define square (lambda (x) (* x x)))

(square 21) ; expect square

(square (+ 2 5)) ; expect 441

(square (square 3)) ; expect 49

; expect 81 
(define (sum-of-squares x y)
  (+ (square x) (square y)))

; expect sum-of-squares 
(sum-of-squares 3 4)

; expect 25 
(define (f a)
  (sum-of-squares (+ a 1) (* a 2)))

(f 5) ; expect f

; expect 136 
(define (abs x)
  (cond ((> x 0) x)
        ((= x 0) 0)
        ((< x 0) (- x))))

(abs -3) ; expect abs

(abs 0) ; expect 3

(abs 3) ; expect 0

; expect 3 
(define (a-plus-abs-b a b)
  ((if (> b 0) + -) a b))

; expect a-plus-abs-b 
(a-plus-abs-b 3 -2)

; expect 5 
(define (sqrt-iter guess x)
  (if (good-enough? guess x)
      guess
      (sqrt-iter (improve guess x) x)))

; expect sqrt-iter 
(define (improve guess x)
  (average guess (/ x guess)))

; expect improve 
(define (average x y) (/ (+ x y) 2))

; expect average 
(define (good-enough? guess x)
  (< (abs (- (square guess) x)) 0.001))

; expect good-enough? 
(define (sqrt x) (sqrt-iter 1 x))

(sqrt 9) ; expect sqrt

; expect 3.00009155413138 
(sqrt (+ 100 37))

; expect 11.704699917758145 
(sqrt (+ (sqrt 2) (sqrt 3)))

; expect 1.7739279023207892 
(square (sqrt 1000))

; expect 1000.000369924366 
(define (sqrt x)
  (define (good-enough? guess)
    (< (abs (- (square guess) x)) 0.001))
  (define (improve guess)
    (average guess (/ x guess)))
  (define (sqrt-iter guess)
    (if (good-enough? guess)
        guess
        (sqrt-iter (improve guess))))
  (sqrt-iter 1))

(sqrt 9) ; expect sqrt

; expect 3.00009155413138 
(sqrt (+ 100 37))

; expect 11.704699917758145 
(sqrt (+ (sqrt 2) (sqrt 3)))

; expect 1.7739279023207892 
(square (sqrt 1000))

; expect 1000.000369924366 
(define (cube x) (* x x x))

; expect cube 
(define (sum term a next b)
  (if (> a b)
      0
      (+ (term a) (sum term (next a) next b))))

(define (inc n) (+ n 1)) ; expect sum

; expect inc 
(define (sum-cubes a b)
  (sum cube a inc b))

(sum-cubes 1 10) ; expect sum-cubes

(define (identity x) x) ; expect 3025

; expect identity 
(define (sum-integers a b)
  (sum identity a inc b))

; expect sum-integers 
(sum-integers 1 10)

; expect 55 
((lambda (x y z) (+ x y (square z)))
 1
 2
 3)

; expect 12 
(define (f x y)
  (let ((a (+ 1 (* x y)))
        (b (- 1 y)))
    (+ (* x (square a)) (* y b) (* a b))))

(f 3 4) ; expect f

(define x 5) ; expect 456

; expect x 
(+ (let ((x 3))
     (+ x (* x 10)))
   x)

; expect 38 
(let ((x 3)
      (y (+ x 2)))
  (* x y))

; expect 21 
(define (add-rat x y)
  (make-rat
   (+ (* (numer x) (denom y))
      (* (numer y) (denom x)))
   (* (denom x) (denom y))))

; expect add-rat 
(define (sub-rat x y)
  (make-rat
   (- (* (numer x) (denom y))
      (* (numer y) (denom x)))
   (* (denom x) (denom y))))

; expect sub-rat 
(define (mul-rat x y)
  (make-rat (* (numer x) (numer y))
            (* (denom x) (denom y))))

; expect mul-rat 
(define (div-rat x y)
  (make-rat (* (numer x) (denom y))
            (* (denom x) (numer y))))

; expect div-rat 
(define (equal-rat? x y)
  (= (* (numer x) (denom y))
     (* (numer y) (denom x))))

; expect equal-rat? 
(define x (cons 1 2))

(car x) ; expect x

(cdr x) ; expect 1

(define x (cons 1 2)) ; expect 2

(define y (cons 3 4)) ; expect x

(define z (cons x y)) ; expect y

(car (car z)) ; expect z

(car (cdr z)) ; expect 1

z ; expect 3

; expect ((1 . 2) 3 . 4) 
(define (make-rat n d) (cons n d))

; expect make-rat 
(define (numer x) (car x))

; expect numer 
(define (denom x) (cdr x))

; expect denom 
(define (print-rat x)
  (display (numer x))
  (display (quote /))
  (display (denom x))
  (newline))

; expect print-rat 
(define one-half (make-rat 1 2))

(print-rat one-half) ; expect one-half

; expect  
(define one-third (make-rat 1 3))

; expect one-third 
(print-rat (add-rat one-half one-third))

; expect  
(print-rat (mul-rat one-half one-third))

; expect  
(print-rat (add-rat one-third one-third))

; expect  
(define (gcd a b)
  (if (= b 0) a (gcd b (remainder a b))))

; expect gcd 
(define (make-rat n d)
  (let ((g (gcd n d)))
    (cons (/ n g) (/ d g))))

; expect make-rat 
(print-rat (add-rat one-third one-third))

; expect  
(define one-through-four
  (list 1 2 3 4))

one-through-four ; expect one-through-four

; expect (1 2 3 4) 
(car one-through-four)

(cdr one-through-four) ; expect 1

; expect (2 3 4) 
(car (cdr one-through-four))

(cons 10 one-through-four) ; expect 2

; expect (10 1 2 3 4) 
(cons 5 one-through-four)

; expect (5 1 2 3 4) 
(define (map proc items)
  (if (null? items)
      nil
      (cons (proc (car items))
            (map proc (cdr items)))))

; expect map 
(map abs (list -10 2.5 -11.6 17))

; expect (10 2.5 11.6 17) 
(map (lambda (x) (* x x))
     (list 1 2 3 4))

; expect (1 4 9 16) 
(define (scale-list items factor)
  (map (lambda (x) (* x factor)) items))

; expect scale-list 
(scale-list (list 1 2 3 4 5) 10)

; expect (10 20 30 40 50) 
(define (count-leaves x)
  (cond ((null? x) 0)
        ((not (pair? x)) 1)
        (else
         (+ (count-leaves (car x))
            (count-leaves (cdr x))))))

; expect count-leaves 
(define x (cons (list 1 2) (list 3 4)))

(count-leaves x) ; expect x

(count-leaves (list x x)) ; expect 4

; expect 8 
(define (odd? x) (= 1 (remainder x 2)))

; expect odd? 
(define (filter predicate sequence)
  (cond ((null? sequence) nil)
        ((predicate (car sequence))
         (cons (car sequence)
               (filter predicate (cdr sequence))))
        (else (filter predicate (cdr sequence)))))

; expect filter 
(filter odd? (list 1 2 3 4 5))

; expect (1 3 5) 
(define (accumulate op initial sequence)
  (if (null? sequence)
      initial
      (op (car sequence)
          (accumulate op initial (cdr sequence)))))

; expect accumulate 
(accumulate + 0 (list 1 2 3 4 5))

; expect 15 
(accumulate * 1 (list 1 2 3 4 5))

; expect 120 
(accumulate cons nil (list 1 2 3 4 5))

; expect (1 2 3 4 5) 
(define (enumerate-interval low high)
  (if (> low high)
      nil
      (cons low
            (enumerate-interval (+ low 1) high))))

; expect enumerate-interval 
(enumerate-interval 2 7)

; expect (2 3 4 5 6 7) 
(define (enumerate-tree tree)
  (cond ((null? tree) nil)
        ((not (pair? tree)) (list tree))
        (else
         (append (enumerate-tree (car tree))
                 (enumerate-tree (cdr tree))))))

; expect enumerate-tree 
(enumerate-tree
 (list 1 (list 2 (list 3 4)) 5))

(define a 1) ; expect (1 2 3 4 5)

(define b 2) ; expect a

(list a b) ; expect b

; expect (1 2) 
(list (quote a) (quote b))

(list (quote a) b) ; expect (a b)

(car (quote (a b c))) ; expect (a 2)

(cdr (quote (a b c))) ; expect a

; expect (b c) 
(define (memq item x)
  (cond ((null? x) #f)
        ((equal? item (car x)) x)
        (else (memq item (cdr x)))))

; expect memq 
(memq (quote apple)
      (quote (pear banana prune)))

; expect #f 
(memq (quote apple)
      (quote (x (apple sauce) y apple pear)))

; expect (apple pear) 
(define (my-equal? x y)
  (cond
   ((pair? x)
    (and (pair? y)
         (my-equal? (car x) (car y))
         (my-equal? (cdr x) (cdr y))))
   ((null? x) (null? y))
   (else (equal? x y))))

; expect my-equal? 
(my-equal? (quote (1 2 (three)))
           (quote (1 2 (three))))

; expect #t 
(my-equal? (quote (1 2 (three)))
           (quote (1 2 three)))

; expect #f 
(my-equal? (quote (1 2 three))
           (quote (1 2 (three))))

; expect #f 
(define double (lambda (x) (* 2 x)))

(double 5) ; expect double

; expect 10 
(define compose
  (lambda (f g) (lambda (x) (f (g x)))))

; expect compose 
((compose list double) 5)

; expect (10) 
(define apply-twice
  (lambda (f) (compose f f)))

; expect apply-twice 
((apply-twice double) 5)

; expect 20 
((apply-twice (apply-twice double)) 5)

; expect 80 
(define fact
  (lambda (n)
          (if (<= n 1) 1 (* n (fact (- n 1))))))

(fact 3) ; expect fact

(fact 50) ; expect 6

; expect 30414093201713378043612608166064768844377641568960512000000000000 
(define (combine f)
  (lambda (x y)
          (if (null? x)
              nil
              (f (list (car x) (car y))
                 ((combine f) (cdr x) (cdr y))))))

; expect combine 
(define zip (combine cons))

; expect zip 
(zip (list 1 2 3 4) (list 5 6 7 8))

; expect ((1 5) (2 6) (3 7) (4 8)) 
(define riff-shuffle
  (lambda (deck)
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
           (define mid
             (lambda (seq) (/ (length seq) 2)))
           ((combine append)
            (take (mid deck) deck)
            (drop (mid deck) deck)))))

; expect riff-shuffle 
(riff-shuffle (list 1 2 3 4 5 6 7 8))

; expect (1 5 2 6 3 7 4 8) 
((apply-twice riff-shuffle)
 (list 1 2 3 4 5 6 7 8))

; expect (1 3 5 7 2 4 6 8) 
(riff-shuffle
 (riff-shuffle
  (riff-shuffle (list 1 2 3 4 5 6 7 8))))

; expect (1 2 3 4 5 6 7 8) 
(apply square (quote (2)))

(apply + (quote (1 2 3 4))) ; expect 4

; expect 10 
(apply (if #f + append)
       (quote ((1 2) (3 4))))

(if 0 1 2) ; expect (1 2 3 4)

(if (quote nil) 1 2) ; expect 1

(or #f #t) ; expect 1

(or) ; expect #t

(and) ; expect #f

(or 1 2 3) ; expect #t

(and 1 2 3) ; expect 1

(and #f (/ 1 0)) ; expect 3

(and #t (/ 1 0)) ; expect #f

(or 3 (/ 1 0)) ; expect SchemeError

(or #f (/ 1 0)) ; expect 3

; expect SchemeError 
(or (quote hello) (quote world))

(if nil 1 2) ; expect hello

(if 0 1 2) ; expect 1

(if (or #f #f #f) 1 2) ; expect 1

(define (loop) (loop)) ; expect 2

; expect loop 
(cond (#f (loop))
      (12))

; expect 12 
((lambda (x) (display x) (newline) x)
 2)

(define g (mu nil x)) ; expect 2

(define (high f x) (f)) ; expect g

(high g 2) ; expect high

; expect 2 
(define (print-and-square x)
  (print x)
  (square x))

; expect print-and-square 
(print-and-square 12)

(/ 1 0) ; expect 144

; expect SchemeError 
(define addx (mu (x) (+ x y)))

; expect addx 
(define add2xy
  (lambda (x y) (addx (+ x x))))

(add2xy 3 7) ; expect add2xy

; expect 13 
(let ((x 2))
  ((begin (define x (+ x 1)) +)
   3
   (begin (define x (+ x 1)) x)))

; expect 7 
(define (len s)
  (if (eq? s (quote nil))
      0
      (+ 1 (len (cdr s)))))

(len (quote (1 2 3 4))) ; expect len

; expect 4 
(define (sum n total)
  (if (zero? n)
      total
      (sum (- n 1) (+ n total))))

(sum 1001 0) ; expect sum

; expect 501501 
(define (sum n total)
  (cond ((zero? n) total)
        (else (sum (- n 1) (+ n total)))))

(sum 1001 0) ; expect sum

; expect 501501 
(define (sum n total)
  (begin 2
         3
         (if (zero? n)
             total
             (and 2
                  3
                  (or #f
                      (begin 2
                             3
                             (let ((m n))
                               (sum (- m 1) (+ m total)))))))))

(exit) ; expect 501501

; expect SchemeError 
(define (map f lst)
  (if (null? lst)
      nil
      (cons (f (car lst)) (map f (cdr lst)))))

; expect map 
(define-macro (for formal iterable body)
  (list (quote map)
        (list (quote lambda)
              (list formal)
              body)
        iterable))

; expect for 
(for i
     (quote (1 2 3))
     (if (= i 1) 0 i))

; expect (0 2 3) 
(define (cadr s) (car (cdr s)))

; expect cadr 
(define (cars s) (map car s))

; expect cars 
(define (cadrs s) (map cadr s))

; expect cadrs 
(define-macro (leet bindings expr)
  (cons
   (list (quote lambda)
         (cars bindings)
         expr)
   (cadrs bindings)))

; expect leet 
(define (square x) (* x x))

; expect square 
(define (hyp a b)
  (leet ((a2 (square a)) (b2 (square b)))
        (sqrt (+ a2 b2))))

(hyp 3 4) ; expect hyp