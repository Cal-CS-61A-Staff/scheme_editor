+
; expect #[+] 

display
; expect #[display] 

hello
; expect SchemeError 

2
; expect 2 

2
; expect 2 

2
; expect 2 

2
; expect 2 

2
; expect 2 

2
; expect 2 

(+ 2 2)
; expect 4 

(+ (+ 2 2) (+ 1 3) (* 1 4))
; expect 12 

(yolo)
; expect SchemeError 

(+ 2 3)
; expect 5 

(* (+ 3 2) (+ 1 7))
; expect 40 

(1 2)
; expect SchemeError 

(1 (print 0))
; expect SchemeError 

(+)
; expect 0 

(odd? 13)
; expect #t 

(car (list 1 2 3 4))
; expect 1 

(car car)
; expect SchemeError 

(odd? 1 2 3)
; expect SchemeError 

(+ (+ 1) (* 2 3) (+ 5) (+ 6 (+ 7)))
; expect 25 

(*)
; expect 1 

(-)
; expect SchemeError 

(car (cdr (cdr (list 1 2 3 4))))
; expect 3 

(car cdr (list 1))
; expect SchemeError 

(* (car (cdr (cdr (list 1 2 3 4)))) (car (cdr (list 1 2 3 4))))
; expect 6 

(* (car (cdr (cdr (list 1 2 3 4)))) (cdr (cdr (list 1 2 3 4))))
; expect SchemeError 

(+ (/ 1 0))
; expect SchemeError 

((/ 1 0) (print 5))
; expect SchemeError 

(null? (print 5))
; expect #f 

(define size 2)
; expect size 

size
; expect 2 

(define x (+ 2 3))
; expect x 

x
; expect 5 

(define x (+ 2 7))
; expect x 

x
; expect 9 

(eval (define tau 6.28))
; expect 6.28 

(define pi 3.14159)
; expect pi 

(define radius 10)
; expect radius 

(define area (* pi (* radius radius)))
; expect area 

area
; expect 314.159 

(define radius 100)
; expect radius 

radius
; expect 100 

area
; expect 314.159 

(define 0 1)
; expect SchemeError 

(define error (/ 1 0))
; expect SchemeError 

(quote hello)
; expect hello 

(quote hello)
; expect hello 

(quote (1 2))
; expect (1 2) 

(quote (1 2))
; expect (1 2) 

(quote (1 . 2))
; expect (1 . 2) 

(quote (1 2))
; expect (1 2) 

(car (quote (1 2 3)))
; expect 1 

(cdr (quote (1 2)))
; expect (2) 

(car (car (quote ((1)))))
; expect 1 

(quote 3)
; expect 3 

(eval (cons (quote car) (quote ((quote (4 2))))))
; expect 4 

(quasiquote (1 2 3))
; expect (1 2 3) 

(define a 2)
; expect a 

(quasiquote (unquote a))
; expect 2 

(quasiquote (a b c))
; expect (a b c) 

(quasiquote ((unquote a) b c))
; expect (2 b c) 

(quasiquote ((unquote a) (unquote b) c))
; expect SchemeError 

(quasiquote ((unquote (+ (unquote a) (unquote a))) b))
; expect SchemeError 

(quasiquote (quasiquote (1 2 (+ 3 4))))
; expect (quasiquote (1 2 (+ 3 4))) 

(quasiquote (1 (unquote (cons a (quasiquote (b (unquote (+ 1 2))))))))
; expect (1 (2 b 3)) 

(begin (+ 2 3) (+ 5 6))
; expect 11 

(begin (define x 3) x)
; expect 3 

(begin 30 (quote (+ 2 2)))
; expect (+ 2 2) 

(define x 0)
; expect x 

(begin 42 (define x (+ x 1)))
; expect x 

x
; expect 1 

(begin 30 (quote hello))
; expect hello 

(begin (define x 3) (cons x (quote (y z))))
; expect (3 y z) 

(begin (define x 3) (cons x (quote (x z))))
; expect (3 x z) 

(define x 0)
; expect x 

(begin (define x (+ x 1)) (define x (+ x 10)) (define x (+ x 100)) (define x (+ x 1000)))
; expect x 

x
; expect 1111 

(lambda (x y) (+ x y))
; expect (lambda (x y) (+ x y)) 

(lambda (x) (+ x) (+ x x))
; expect (lambda (x) (+ x) (+ x x)) 

(lambda (x))
; expect SchemeError 

(lambda nil 2)
; expect (lambda () 2) 

(define (f) (+ 2 2))
; expect f 

f
; expect (lambda () (+ 2 2)) 

(define (f x) (* x x))
; expect f 

f
; expect (lambda (x) (* x x)) 

(define (foo x) 1 2 3 4 5)
; expect foo 

foo
; expect (lambda (x) 1 2 3 4 5) 

(define (foo) (/ 1 0))
; expect foo 

foo
; expect (lambda () (/ 1 0)) 

(define (square x) (* x x))
; expect square 

square
; expect (lambda (x) (* x x)) 

(square 21)
; expect 441 

square
; expect (lambda (x) (* x x)) 

(define square (lambda (x) (* x x)))
; expect square 

(square (square 21))
; expect 194481 

((lambda (x) (list x (list (quote quote) x))) (quote (lambda (x) (list x (list (quote quote) x)))))
; expect ((lambda (x) (list x (list (quote quote) x))) (quote (lambda (x) (list x (list (quote quote) x))))) 

(define (outer x y) (define (inner z x) (+ x (* y 2) (* z 3))) (inner x 10))
; expect outer 

(outer 1 2)
; expect 17 

(define (outer-func x y) (define (inner z x) (+ x (* y 2) (* z 3))) inner)
; expect outer-func 

((outer-func 1 2) 1 10)
; expect 17 

(define square (lambda (x) (* x x)))
; expect square 

(define (sum-of-squares x y) (+ (square x) (square y)))
; expect sum-of-squares 

(sum-of-squares 3 4)
; expect 25 

(define double (lambda (x) (* 2 x)))
; expect double 

(define compose (lambda (f g) (lambda (x) (f (g x)))))
; expect compose 

(define apply-twice (lambda (f) (compose f f)))
; expect apply-twice 

((apply-twice double) 5)
; expect 20 

(and)
; expect #t 

(and 1 #f)
; expect #f 

(and (+ 1 1) 1)
; expect 1 

(and #f 5)
; expect #f 

(and 4 5 (+ 3 3))
; expect 6 

(and #t #f 42 (/ 1 0))
; expect #f 

(not (and #f))
; expect #t 

(and 3 2 #f)
; expect #f 

(and 3 2 1)
; expect 1 

(and 3 #f 5)
; expect #f 

(and 0 1 2 3)
; expect 3 

(define (true-fn) #t)
; expect true-fn 

(and (true-fn))
; expect #t 

(define x #f)
; expect x 

(and x #t)
; expect #f 

(define x 0)
; expect x 

(and (define x (+ x 1)) (define x (+ x 10)) (define x (+ x 100)) (define x (+ x 1000)))
; expect x 

x
; expect 1111 

(define x 0)
; expect x 

(and (define x (+ x 1)) (define x (+ x 10)) #f (define x (+ x 100)) (define x (+ x 1000)))
; expect #f 

x
; expect 11 

(define (no-mutation) (and #t #t #t #t))
; expect no-mutation 

no-mutation
; expect (lambda () (and #t #t #t #t)) 

(no-mutation)
; expect #t 

no-mutation
; expect (lambda () (and #t #t #t #t)) 

(or)
; expect #f 

(or (+ 1 1))
; expect 2 

(not (or #f))
; expect #t 

(define (t) #t)
; expect t 

(or (t) 3)
; expect #t 

(or 5 2 1)
; expect 5 

(or #f (- 1 1) 1)
; expect 0 

(or 4 #t (/ 1 0))
; expect 4 

(or 0 1 2)
; expect 0 

(or (quote a) #f)
; expect a 

(or (< 2 3) (> 2 3) 2 (quote a))
; expect #t 

(or (< 2 3) 2)
; expect #t 

(define (false-fn) #f)
; expect false-fn 

(or (false-fn) (quote yay))
; expect yay 

(define x 0)
; expect x 

(or (begin (define x (+ x 1)) #f) (begin (define x (+ x 10)) #f) (begin (define x (+ x 100)) #f) (begin (define x (+ x 1000)) #f))
; expect #f 

x
; expect 1111 

(define x 0)
; expect x 

(or (begin (define x (+ x 1)) #f) (begin (define x (+ x 10)) #f) #t (begin (define x (+ x 100)) #f) (begin (define x (+ x 1000)) #f))
; expect #t 

x
; expect 11 

(define (no-mutation) (or #f #f #f #f))
; expect no-mutation 

no-mutation
; expect (lambda () (or #f #f #f #f)) 

(no-mutation)
; expect #f 

no-mutation
; expect (lambda () (or #f #f #f #f)) 

(define (greater-than-5 x) (if (> x 5) #t #f))
; expect greater-than-5 

(define (other y) (or (greater-than-5 y) #f))
; expect other 

(other 2)
; expect #f 

(other 6)
; expect #t 

(define (other y) (and (greater-than-5 y) #t))
; expect other 

(other 2)
; expect #f 

(other 6)
; expect #t 

(cond ((> 2 3) 5) ((> 2 4) 6) ((< 2 5) 7) (else 8))
; expect 7 

(cond ((> 2 3) 5) ((> 2 4) 6) (else 8))
; expect 8 

(if 0 1 2)
; expect 1 

(if #f 1 (if #t 2 3))
; expect 2 

(if (= 1 2) (/ 1 0) (quote a))
; expect a 

(cond ((> 2 3) 5) ((> 2 4) 6) ((< 2 5) 7))
; expect 7 

(cond ((> 2 3) (display (quote oops)) (newline)) (else 9))
; expect 9 

(cond ((< 2 1)) ((> 3 2)) (else 5))
; expect #t 

(cond (#f 1))
; expect  

(cond ((= 4 3) (quote nope)) ((= 4 4) (quote hi)) (else (quote wat)))
; expect hi 

(cond ((= 4 3) (quote wat)) ((= 4 4)) (else (quote hm)))
; expect #t 

(cond ((= 4 4) (+ 40 2)) (else (quote wat) 0))
; expect 42 

(cond (12))
; expect 12 

(cond ((= 4 3)) ((quote hi)))
; expect hi 

(eval (cond (#f 1) (#f 2)))
; expect  

(cond (0 (quote yea)) (else (quote nay)))
; expect yea 

(define x 0)
; expect x 

(define y 0)
; expect y 

(define z 0)
; expect z 

(cond (#t (define x (+ x 1)) (define y (+ y 1)) (define z (+ z 1))) (else (define x (- x 5)) (define y (- y 5)) (define z (- z 5))))
; expect z 

(list x y z)
; expect (1 1 1) 

(define (print-and-false val) (print val) #f)
; expect print-and-false 

(cond ((print-and-false (quote cond1))) ((print-and-false (quote cond2))) ((print-and-false (quote cond3))) ((print-and-false (quote cond4))))
; expect  

(define (print-and-true val) (print val) #t)
; expect print-and-true 

(cond ((print-and-false (quote cond1))) ((print-and-false (quote cond2))) ((print-and-true (quote cond3))) ((print-and-false (quote cond4))))
; expect #t 

(define x 1)
; expect x 

(let ((x 5)) (+ x 3))
; expect 8 

x
; expect 1 

(let ((a 1) (b a)) b)
; expect SchemeError 

(let ((x 5)) (let ((x 2) (y x)) (+ y (* x 2))))
; expect 9 

(define (square x) (* x x))
; expect square 

(define (f x y) (let ((a (+ 1 (* x y))) (b (- 1 y))) (+ (* x (square a)) (* y b) (* a b))))
; expect f 

(f 3 4)
; expect 456 

(define x 3)
; expect x 

(define y 4)
; expect y 

(let ((x (+ y 2)) (y (+ x 2))) (cons x y))
; expect (6 . 5) 

(let ((x (quote hello))) x)
; expect hello 

(let ((a 1) (b 2) (c 3)) (+ a b c))
; expect 6 

(define z 0)
; expect z 

(let ((a (define z (+ z 1)))) z)
; expect 1 

(let ((x 1) (y 3)) (define x (+ x 1)) (cons x y))
; expect (2 . 3) 

(let ((a 1 1)) a)
; expect SchemeError 

(let ((a 1) (2 2)) a)
; expect SchemeError 

(define y 1)
; expect y 

(define f (mu (x) (+ x y)))
; expect f 

(define g (lambda (x y) (f (+ x x))))
; expect g 

(g 3 7)
; expect 13 

(define h (mu nil x))
; expect h 

(define (high fn x) (fn))
; expect high 

(high h 2)
; expect 2 

(define (f x) (mu nil (lambda (y) (+ x y))))
; expect f 

(define (g x) (((f (+ x 1))) (+ x 2)))
; expect g 

(g 3)
; expect 8 

(mu nil)
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
; expect () 

(load (quote questions))
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
; expect None 

(let-to-lambda 1)
; expect 1 

(let-to-lambda (quote a))
; expect a 

(let-to-lambda (quote (+ 1 2)))
; expect (+ 1 2) 

(let-to-lambda (quote (let ((a 1) (b 2)) (+ a b))))
; expect ((lambda (a b) (+ a b)) 1 2) 

(load (quote questions))
; expect None 

(quote (quoted expressions remain the same))
; expect (quoted expressions remain the same) 

(let-to-lambda (quote (quote (let ((a 1) (b 2)) (+ a b)))))
; expect (quote (let ((a 1) (b 2)) (+ a b))) 

(load (quote questions))
; expect None 

(quote (lambda parameters not affected but body affected))
; expect (lambda parameters not affected but body affected) 

(let-to-lambda (quote (lambda (let a b) (+ let a b))))
; expect (lambda (let a b) (+ let a b)) 

(let-to-lambda (quote (lambda (x) a (let ((a x)) a))))
; expect (lambda (x) a ((lambda (a) a) x)) 

(load (quote questions))
; expect None 

(let-to-lambda (quote (let ((a (let ((a 2)) a)) (b 2)) (+ a b))))
; expect ((lambda (a b) (+ a b)) ((lambda (a) a) 2) 2) 

(let-to-lambda (quote (let ((a 1)) (let ((b a)) b))))
; expect ((lambda (a) ((lambda (b) b) a)) 1) 

(let-to-lambda (quote (+ 1 (let ((a 1)) a))))
; expect (+ 1 ((lambda (a) a) 1)) 

(define (map f lst) (if (null? lst) nil (cons (f (car lst)) (map f (cdr lst)))))
; expect map 

(define-macro (for formal iterable body) (list (quote map) (list (quote lambda) (list formal) body) iterable))
; expect for 

(for i (quote (1 2 3)) (if (= i 1) 0 i))
; expect (0 2 3) 

(define (map f lst) (if (null? lst) nil (cons (f (car lst)) (map f (cdr lst)))))
; expect map 

(define (cadr s) (car (cdr s)))
; expect cadr 

(define (cars s) (map car s))
; expect cars 

(define (cadrs s) (map cadr s))
; expect cadrs 

(define-macro (leet bindings expr) (cons (list (quote lambda) (cars bindings) expr) (cadrs bindings)))
; expect leet 

(define (square x) (* x x))
; expect square 

(define (hyp a b) (leet ((a2 (square a)) (b2 (square b))) (sqrt (+ a2 b2))))
; expect hyp 

(hyp 3 4)
; expect 5.0 

(define (map f lst) (if (null? lst) nil (cons (f (car lst)) (map f (cdr lst)))))
; expect map 

(define-macro wat?)
; expect SchemeError 

(define-macro woah okay)
; expect SchemeError 

(define-macro (hello world))
; expect SchemeError 

(define-macro (5) (cons 1 2))
; expect SchemeError 

(define-macro (name) (body))
; expect name 

name
; expect (lambda () (body)) 

(name)
; expect SchemeError 

(quote (1 2 3 4 5 . 6))
; expect (1 2 3 4 5 . 6) 

(quote (1 2))
; expect (1 2) 

(quote (1 . 2))
; expect (1 . 2) 

+
; expect #[+] 

cat
; expect SchemeError 

floor
; expect #[floor] 

(print "cat")
; expect  

(display "cat")
; expect  

(newline)
; expect  

nil
; expect () 

(quote nil)
; expect () 

begin
; expect SchemeError 

(sqrt 9)
; expect 3.0 

3
; expect 3 

(= 3 3)
; expect #t 

(quote #f)
; expect #f 

(quote #f)
; expect #f 

(if (quote #f) (print "err") (print "success"))
; expect  

(= (sqrt 9) 3)
; expect #t 

(= (sqrt 9) 3)
; expect #t 

(/ 1 0)
; expect SchemeError 

(cat dog)
; expect SchemeError 

nil
; expect () 

(sqrt -1)
(* (+) (*))
; expect 0 

(+ (*) (*) (*))
; expect 3 

(/)
; expect SchemeError 

(/ 2)
; expect 0.5 

(odd? #f)
; expect SchemeError 

(-)
; expect SchemeError 

(floor 2.5)
; expect 2 

(define cat dog)
; expect SchemeError 

(define cat cat)
; expect SchemeError 

(define a b c)
; expect SchemeError 

(define (a) b c)
; expect a 

(a)
; expect SchemeError 

(define a)
; expect SchemeError 

(define)
; expect SchemeError 

define
; expect SchemeError 

(define (scope) (define define 5) (+ define define))
; expect scope 

(scope)
; expect 10 

(define (scope) (define (unquote cat) 5) (unquote 6))
; expect scope 

(scope)
; expect 5 

(unquote cat)
; expect SchemeError 

(define cat (quote cat))
; expect cat 

(eval cat)
; expect cat 

(eval (eval (eval cat)))
; expect cat 

(eval eval)
; expect #[eval] 

(define (id x) x)
; expect id 

(define dog 5)
; expect dog 

(apply id (quote ((quote dog))))
; expect (quote dog) 

(apply id (quote (dog)))
; expect dog 

(apply eval (quote ((quote (quote (dog))))))
; expect (quote (dog)) 

(apply eval (list (quote (quote (dog)))))
; expect (dog) 

(apply eval (quote ((quote (quote dog)))))
; expect (quote dog) 

(apply eval (quote (dog)))
; expect 5 

(define (x a b c) (+ a b c))
; expect x 

(define y +)
; expect y 

(= (x 4 66 1) (y 4 66 1))
; expect #t 

(eq? x y)
; expect #f 

(define z +)
; expect z 

(eq? y z)
; expect #t 

((begin (print "cat") +) 2 3 4)
; expect 9 

((print "1") (print "2"))
; expect SchemeError 

(define x 1)
; expect x 

(define x (+ 1 x))
; expect x 

x
; expect 2 

(define 2 x)
; expect SchemeError 

(define #t #f)
; expect SchemeError 

(define cat 5)
; expect cat 

cat
; expect 5 

cat
; expect 5 

(quote (car 5))
; expect (car 5) 

(quote (print "cat"))
; expect (print "cat") 

(quote (quote (print (quote cat))))
; expect (quote (print (quote cat))) 

(eval (quote (print "cat")))
; expect  

(eval (quote ((print "cat"))))
; expect SchemeError 

(quasiquote (+ 1 2 3 4))
; expect (+ 1 2 3 4) 

(quasiquote (1 2 3 (unquote (+ 4 5))))
; expect (1 2 3 9) 

(quasiquote (1 2 3 unquote (+ 4 5)))
; expect (1 2 3 . 9) 

(quasiquote (1 2 3 unquote + 4 5))
; expect SchemeError 

(quasiquote (1 2 3 (quasiquote (4 5 (unquote (+ 6 7 8))))))
; expect (1 2 3 (quasiquote (4 5 (unquote (+ 6 7 8))))) 

(quasiquote (1 2 3 (quasiquote (4 5 unquote + 6 7 8))))
; expect (1 2 3 (quasiquote (4 5 unquote + 6 7 8))) 

(begin)
; expect SchemeError 

((lambda (x) (* x x)) 2)
; expect 4 

(define x 6)
; expect x 

((lambda (y) (print y) (* x y)) 2)
; expect 12 

(define x 7)
; expect x 

((lambda (y) (print y) (* x y)) 2)
; expect 14 

(lambda (y))
; expect SchemeError 

(define (f x) (+ a b c))
; expect f 

f
; expect (lambda (x) (+ a b c)) 

(define (f x) (define (g y) (+ x y)) g)
; expect f 

g
; expect SchemeError 

(f 5)
; expect (lambda (y) (+ x y)) 

(and)
; expect #t 

(or)
; expect #f 

(and 1 2 3)
; expect 3 

(and 1 2 #f 4)
; expect #f 

(or #f #f 5)
; expect 5 

(or #f #f)
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

(cond (#t (print "5")) (#t (print "6")) (else (print "7")))
; expect  

(cond (#f) ((print "5")) ((print "6")))
; expect  

(let ((cat 1) (dog 2) (elephant 3)) (+ cat dog elephant))
; expect 6 

elephant
; expect SchemeError 

(define cat 1)
; expect cat 

(let ((cat 2)) (+ 1 cat))
; expect 3 

cat
; expect 1 

(define cat 1)
; expect cat 

(let ((cat 2) (dog (+ 1 cat))) dog)
; expect 2 

(define f (mu (x) (print x) (if (> x 0) (begin y (define y x) (f (- x 1))) 1)))
; expect f 

(define y 5)
; expect y 

(f y)
; expect 1 

(define (tailcall x) (if (> x 0) (tailcall (- x 1)) (print "wow")))
; expect tailcall 

(tailcall 10000)
; expect  

(define-macro (dotwice expr) (list (quote begin) expr expr))
; expect dotwice 

(dotwice (print 5))
; expect  

(define-macro (alwaysprint5 expr) (list print 5))
; expect alwaysprint5 

(alwaysprint5 (print (/ 1 0)))
; expect  

10
; expect 10 

(+ 137 349)
; expect 486 

(- 1000 334)
; expect 666 

(* 5 99)
; expect 495 

(/ 10 5)
; expect 2 

(+ 2.7 10)
; expect 12.7 

(+ 21 35 12 7)
; expect 75 

(* 25 4 12)
; expect 1200 

(+ (* 3 5) (- 10 6))
; expect 19 

(+ (* 3 (+ (* 2 4) (+ 3 5))) (+ (- 10 7) 6))
; expect 57 

(+ (* 3 (+ (* 2 4) (+ 3 5))) (+ (- 10 7) 6))
; expect 57 

(define size 2)
; expect size 

size
; expect 2 

(* 5 size)
; expect 10 

(define pi 3.14159)
; expect pi 

(define radius 10)
; expect radius 

(* pi (* radius radius))
; expect 314.159 

(define circumference (* 2 pi radius))
; expect circumference 

circumference
; expect 62.8318 

(define (square x) (* x x))
; expect square 

(square 21)
; expect 441 

(define square (lambda (x) (* x x)))
; expect square 

(square 21)
; expect 441 

(square (+ 2 5))
; expect 49 

(square (square 3))
; expect 81 

(define (sum-of-squares x y) (+ (square x) (square y)))
; expect sum-of-squares 

(sum-of-squares 3 4)
; expect 25 

(define (f a) (sum-of-squares (+ a 1) (* a 2)))
; expect f 

(f 5)
; expect 136 

(define (abs x) (cond ((> x 0) x) ((= x 0) 0) ((< x 0) (- x))))
; expect abs 

(abs -3)
; expect 3 

(abs 0)
; expect 0 

(abs 3)
; expect 3 

(define (a-plus-abs-b a b) ((if (> b 0) + -) a b))
; expect a-plus-abs-b 

(a-plus-abs-b 3 -2)
; expect 5 

(define (sqrt-iter guess x) (if (good-enough? guess x) guess (sqrt-iter (improve guess x) x)))
; expect sqrt-iter 

(define (improve guess x) (average guess (/ x guess)))
; expect improve 

(define (average x y) (/ (+ x y) 2))
; expect average 

(define (good-enough? guess x) (< (abs (- (square guess) x)) 0.001))
; expect good-enough? 

(define (sqrt x) (sqrt-iter 1 x))
; expect sqrt 

(sqrt 9)
; expect 3.00009155413138 

(sqrt (+ 100 37))
; expect 11.704699917758145 

(sqrt (+ (sqrt 2) (sqrt 3)))
; expect 1.7739279023207892 

(square (sqrt 1000))
; expect 1000.000369924366 

(define (sqrt x) (define (good-enough? guess) (< (abs (- (square guess) x)) 0.001)) (define (improve guess) (average guess (/ x guess))) (define (sqrt-iter guess) (if (good-enough? guess) guess (sqrt-iter (improve guess)))) (sqrt-iter 1))
; expect sqrt 

(sqrt 9)
; expect 3.00009155413138 

(sqrt (+ 100 37))
; expect 11.704699917758145 

(sqrt (+ (sqrt 2) (sqrt 3)))
; expect 1.7739279023207892 

(square (sqrt 1000))
; expect 1000.000369924366 

(define (cube x) (* x x x))
; expect cube 

(define (sum term a next b) (if (> a b) 0 (+ (term a) (sum term (next a) next b))))
; expect sum 

(define (inc n) (+ n 1))
; expect inc 

(define (sum-cubes a b) (sum cube a inc b))
; expect sum-cubes 

(sum-cubes 1 10)
; expect 3025 

(define (identity x) x)
; expect identity 

(define (sum-integers a b) (sum identity a inc b))
; expect sum-integers 

(sum-integers 1 10)
; expect 55 

((lambda (x y z) (+ x y (square z))) 1 2 3)
; expect 12 

(define (f x y) (let ((a (+ 1 (* x y))) (b (- 1 y))) (+ (* x (square a)) (* y b) (* a b))))
; expect f 

(f 3 4)
; expect 456 

(define x 5)
; expect x 

(+ (let ((x 3)) (+ x (* x 10))) x)
; expect 38 

(let ((x 3) (y (+ x 2))) (* x y))
; expect 21 

(define (add-rat x y) (make-rat (+ (* (numer x) (denom y)) (* (numer y) (denom x))) (* (denom x) (denom y))))
; expect add-rat 

(define (sub-rat x y) (make-rat (- (* (numer x) (denom y)) (* (numer y) (denom x))) (* (denom x) (denom y))))
; expect sub-rat 

(define (mul-rat x y) (make-rat (* (numer x) (numer y)) (* (denom x) (denom y))))
; expect mul-rat 

(define (div-rat x y) (make-rat (* (numer x) (denom y)) (* (denom x) (numer y))))
; expect div-rat 

(define (equal-rat? x y) (= (* (numer x) (denom y)) (* (numer y) (denom x))))
; expect equal-rat? 

(define x (cons 1 2))
; expect x 

(car x)
; expect 1 

(cdr x)
; expect 2 

(define x (cons 1 2))
; expect x 

(define y (cons 3 4))
; expect y 

(define z (cons x y))
; expect z 

(car (car z))
; expect 1 

(car (cdr z))
; expect 3 

z
; expect ((1 . 2) 3 . 4) 

(define (make-rat n d) (cons n d))
; expect make-rat 

(define (numer x) (car x))
; expect numer 

(define (denom x) (cdr x))
; expect denom 

(define (print-rat x) (display (numer x)) (display (quote /)) (display (denom x)) (newline))
; expect print-rat 

(define one-half (make-rat 1 2))
; expect one-half 

(print-rat one-half)
; expect  

(define one-third (make-rat 1 3))
; expect one-third 

(print-rat (add-rat one-half one-third))
; expect  

(print-rat (mul-rat one-half one-third))
; expect  

(print-rat (add-rat one-third one-third))
; expect  

(define (gcd a b) (if (= b 0) a (gcd b (remainder a b))))
; expect gcd 

(define (make-rat n d) (let ((g (gcd n d))) (cons (/ n g) (/ d g))))
; expect make-rat 

(print-rat (add-rat one-third one-third))
; expect  

(define one-through-four (list 1 2 3 4))
; expect one-through-four 

one-through-four
; expect (1 2 3 4) 

(car one-through-four)
; expect 1 

(cdr one-through-four)
; expect (2 3 4) 

(car (cdr one-through-four))
; expect 2 

(cons 10 one-through-four)
; expect (10 1 2 3 4) 

(cons 5 one-through-four)
; expect (5 1 2 3 4) 

(define (map proc items) (if (null? items) nil (cons (proc (car items)) (map proc (cdr items)))))
; expect map 

(map abs (list -10 2.5 -11.6 17))
; expect (10 2.5 11.6 17) 

(map (lambda (x) (* x x)) (list 1 2 3 4))
; expect (1 4 9 16) 

(define (scale-list items factor) (map (lambda (x) (* x factor)) items))
; expect scale-list 

(scale-list (list 1 2 3 4 5) 10)
; expect (10 20 30 40 50) 

(define (count-leaves x) (cond ((null? x) 0) ((not (pair? x)) 1) (else (+ (count-leaves (car x)) (count-leaves (cdr x))))))
; expect count-leaves 

(define x (cons (list 1 2) (list 3 4)))
; expect x 

(count-leaves x)
; expect 4 

(count-leaves (list x x))
; expect 8 

(define (odd? x) (= 1 (remainder x 2)))
; expect odd? 

(define (filter predicate sequence) (cond ((null? sequence) nil) ((predicate (car sequence)) (cons (car sequence) (filter predicate (cdr sequence)))) (else (filter predicate (cdr sequence)))))
; expect filter 

(filter odd? (list 1 2 3 4 5))
; expect (1 3 5) 

(define (accumulate op initial sequence) (if (null? sequence) initial (op (car sequence) (accumulate op initial (cdr sequence)))))
; expect accumulate 

(accumulate + 0 (list 1 2 3 4 5))
; expect 15 

(accumulate * 1 (list 1 2 3 4 5))
; expect 120 

(accumulate cons nil (list 1 2 3 4 5))
; expect (1 2 3 4 5) 

(define (enumerate-interval low high) (if (> low high) nil (cons low (enumerate-interval (+ low 1) high))))
; expect enumerate-interval 

(enumerate-interval 2 7)
; expect (2 3 4 5 6 7) 

(define (enumerate-tree tree) (cond ((null? tree) nil) ((not (pair? tree)) (list tree)) (else (append (enumerate-tree (car tree)) (enumerate-tree (cdr tree))))))
; expect enumerate-tree 

(enumerate-tree (list 1 (list 2 (list 3 4)) 5))
; expect (1 2 3 4 5) 

(define a 1)
; expect a 

(define b 2)
; expect b 

(list a b)
; expect (1 2) 

(list (quote a) (quote b))
; expect (a b) 

(list (quote a) b)
; expect (a 2) 

(car (quote (a b c)))
; expect a 

(cdr (quote (a b c)))
; expect (b c) 

(define (memq item x) (cond ((null? x) #f) ((equal? item (car x)) x) (else (memq item (cdr x)))))
; expect memq 

(memq (quote apple) (quote (pear banana prune)))
; expect #f 

(memq (quote apple) (quote (x (apple sauce) y apple pear)))
; expect (apple pear) 

(define (my-equal? x y) (cond ((pair? x) (and (pair? y) (my-equal? (car x) (car y)) (my-equal? (cdr x) (cdr y)))) ((null? x) (null? y)) (else (equal? x y))))
; expect my-equal? 

(my-equal? (quote (1 2 (three))) (quote (1 2 (three))))
; expect #t 

(my-equal? (quote (1 2 (three))) (quote (1 2 three)))
; expect #f 

(my-equal? (quote (1 2 three)) (quote (1 2 (three))))
; expect #f 

(define double (lambda (x) (* 2 x)))
; expect double 

(double 5)
; expect 10 

(define compose (lambda (f g) (lambda (x) (f (g x)))))
; expect compose 

((compose list double) 5)
; expect (10) 

(define apply-twice (lambda (f) (compose f f)))
; expect apply-twice 

((apply-twice double) 5)
; expect 20 

((apply-twice (apply-twice double)) 5)
; expect 80 

(define fact (lambda (n) (if (<= n 1) 1 (* n (fact (- n 1))))))
; expect fact 

(fact 3)
; expect 6 

(fact 50)
; expect 30414093201713378043612608166064768844377641568960512000000000000 

(define (combine f) (lambda (x y) (if (null? x) nil (f (list (car x) (car y)) ((combine f) (cdr x) (cdr y))))))
; expect combine 

(define zip (combine cons))
; expect zip 

(zip (list 1 2 3 4) (list 5 6 7 8))
; expect ((1 5) (2 6) (3 7) (4 8)) 

(define riff-shuffle (lambda (deck) (begin (define take (lambda (n seq) (if (<= n 0) (quote nil) (cons (car seq) (take (- n 1) (cdr seq)))))) (define drop (lambda (n seq) (if (<= n 0) seq (drop (- n 1) (cdr seq))))) (define mid (lambda (seq) (/ (length seq) 2))) ((combine append) (take (mid deck) deck) (drop (mid deck) deck)))))
; expect riff-shuffle 

(riff-shuffle (list 1 2 3 4 5 6 7 8))
; expect (1 5 2 6 3 7 4 8) 

((apply-twice riff-shuffle) (list 1 2 3 4 5 6 7 8))
; expect (1 3 5 7 2 4 6 8) 

(riff-shuffle (riff-shuffle (riff-shuffle (list 1 2 3 4 5 6 7 8))))
; expect (1 2 3 4 5 6 7 8) 

(apply square (quote (2)))
; expect 4 

(apply + (quote (1 2 3 4)))
; expect 10 

(apply (if #f + append) (quote ((1 2) (3 4))))
; expect (1 2 3 4) 

(if 0 1 2)
; expect 1 

(if (quote nil) 1 2)
; expect 1 

(or #f #t)
; expect #t 

(or)
; expect #f 

(and)
; expect #t 

(or 1 2 3)
; expect 1 

(and 1 2 3)
; expect 3 

(and #f (/ 1 0))
; expect #f 

(and #t (/ 1 0))
; expect SchemeError 

(or 3 (/ 1 0))
; expect 3 

(or #f (/ 1 0))
; expect SchemeError 

(or (quote hello) (quote world))
; expect hello 

(if nil 1 2)
; expect 1 

(if 0 1 2)
; expect 1 

(if (or #f #f #f) 1 2)
; expect 2 

(define (loop) (loop))
; expect loop 

(cond (#f (loop)) (12))
; expect 12 

((lambda (x) (display x) (newline) x) 2)
; expect 2 

(define g (mu nil x))
; expect g 

(define (high f x) (f))
; expect high 

(high g 2)
; expect 2 

(define (print-and-square x) (print x) (square x))
; expect print-and-square 

(print-and-square 12)
; expect 144 

(/ 1 0)
; expect SchemeError 

(define addx (mu (x) (+ x y)))
; expect addx 

(define add2xy (lambda (x y) (addx (+ x x))))
; expect add2xy 

(add2xy 3 7)
; expect 13 

(let ((x 2)) ((begin (define x (+ x 1)) +) 3 (begin (define x (+ x 1)) x)))
; expect 7 

(define (len s) (if (eq? s (quote nil)) 0 (+ 1 (len (cdr s)))))
; expect len 

(len (quote (1 2 3 4)))
; expect 4 

(define (sum n total) (if (zero? n) total (sum (- n 1) (+ n total))))
; expect sum 

(sum 1001 0)
; expect 501501 

(define (sum n total) (cond ((zero? n) total) (else (sum (- n 1) (+ n total)))))
; expect sum 

(sum 1001 0)
; expect 501501 

(define (sum n total) (begin 2 3 (if (zero? n) total (and 2 3 (or #f (begin 2 3 (let ((m n)) (sum (- m 1) (+ m total)))))))))
; expect sum 

(sum 1001 0)
; expect 501501 

(exit)
; expect SchemeError 

(define (map f lst) (if (null? lst) nil (cons (f (car lst)) (map f (cdr lst)))))
; expect map 

(define-macro (for formal iterable body) (list (quote map) (list (quote lambda) (list formal) body) iterable))
; expect for 

(for i (quote (1 2 3)) (if (= i 1) 0 i))
; expect (0 2 3) 

(define (cadr s) (car (cdr s)))
; expect cadr 

(define (cars s) (map car s))
; expect cars 

(define (cadrs s) (map cadr s))
; expect cadrs 

(define-macro (leet bindings expr) (cons (list (quote lambda) (cars bindings) expr) (cadrs bindings)))
; expect leet 

(define (square x) (* x x))
; expect square 

(define (hyp a b) (leet ((a2 (square a)) (b2 (square b))) (sqrt (+ a2 b2))))
; expect hyp 

(hyp 3 4)
; expect 5.000023178253949 

(define (sum n total) (if (zero? n) total (sum (- n 1) (+ n total))))
; expect sum 

(sum 1001 0)
; expect 501501 

(define (sum n total) (if (zero? n) total (if #f 42 (sum (- n 1) (+ n total)))))
; expect sum 

(sum 1001 0)
; expect 501501 

(define (sum n total) (cond ((zero? n) total) ((zero? 0) (sum (- n 1) (+ n total))) (else 42)))
; expect sum 

(sum 1001 0)
; expect 501501 

(define (sum n total) (if (zero? n) total (add n (+ n total))))
; expect sum 

(define add (lambda (x+1 y) (sum (- x+1 1) y)))
; expect add 

(sum 1001 0)
; expect 501501 

(define (sum n total) (if (zero? n) total (let ((n-1 (- n 1))) (sum n-1 (+ n total)))))
; expect sum 

(sum 1001 0)
; expect 501501 

(define (sum n total) (or (and (zero? n) total) (add n (+ n total))))
; expect sum 

(define add (lambda (x+1 y) (sum (- x+1 1) y)))
; expect add 

(sum 1001 0)
; expect 501501 

(define (sum n total) (define add (lambda (x+1 y) (sum (- x+1 1) y))) (or (and (zero? n) total) (add n (+ n total))))
; expect sum 

(sum 1001 0)
; expect 501501 

(define (sum n total) (begin (define add (lambda (x+1 y) (sum (- x+1 1) y))) (or (and (zero? n) total) (add n (+ n total)))))
; expect sum 

(sum 1001 0)
; expect 501501 

