(define (caar x) (car (car x)))
(define (cadr x) (car (cdr x)))
(define (cdar x) (cdr (car x)))
(define (cddr x) (cdr (cdr x)))

; Some utility functions that you may find useful to implement.

(define (cons-all first rests)
    (if (null? rests)
        nil
        (cons (cons first (car rests))
              (cons-all first (cdr rests)))))

(define (zip pairs)
 'replace-this-line)

;; Problem 17
;; Returns a list of two-element lists
(define (enumerate s)
 (define (helper s i)
  (if (null? s) nil
   (cons
    (list i (car s))
    (helper (cdr s) (+ i 1)))))
 (helper s 0))

;; Problem 18
;; List all ways to make change for TOTAL with DENOMS
(define (list-change total denoms)
    (cond
        ((null? denoms) nil)
        ((< total 0) nil)
        ((= total 0) `(nil))
        (else (append
                  (cons-all
                      (car denoms)
                      (list-change (- total (car denoms)) denoms))
                  (list-change total (cdr denoms))))))

;; Problem 19
;; Returns a function that checks if an expression is the special form FORM
(define (check-special form)
 (lambda (expr) (equal? form (car expr))))

(define lambda? (check-special 'lambda))
(define define? (check-special 'define))
(define quoted? (check-special 'quote))
(define let? (check-special 'let))

;; Converts all let special forms in EXPR into equivalent forms using lambda
(define (let-to-lambda expr)
 (cond ((atom? expr)
        ; BEGIN PROBLEM 19
        expr
        ; END PROBLEM 19
 )
  ((quoted? expr)
   ; BEGIN PROBLEM 19
   expr
   ; END PROBLEM 19
  )
  ((or (lambda? expr)
       (define? expr))
   (let ((form (car expr))
         (params (cadr expr))
         (body (cddr expr)))
    ; BEGIN PROBLEM 19
    `(,form ,params . ,(map let-to-lambda body))
    ; END PROBLEM 19
   ))
  ((let? expr)
   (let ((values (cadr expr))
         (body (cddr expr)))
     ; BEGIN PROBLEM 19
     (define names (map car values))
     (define vals (map cadr values))
     (append `((lambda ,names . ,(map let-to-lambda body)) . ,(map let-to-lambda vals)))
     ; END PROBLEM 19
   ))
  (else
   ; BEGIN PROBLEM 19
   (map let-to-lambda expr)
   ; END PROBLEM 19
  )))