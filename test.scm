;; Sequence operations

;; Map f over s.
(define (map f s)
  (if (null? s) 
      nil
      (cons (f (car s))
            (map f 
                 (cdr s)))))
  
;; Filter s by f.
(define (filter f s)
  (if (null? s)
      nil
      (if (f (car s))
          (cons (car s) 
                (filter f (cdr s)))
          (filter f (cdr s)))))

;; Reduce s using f and start value.
(define (reduce f s start)
  (if (null? s) 
      start
      (reduce f
              (cdr s)
              (f start (car s)))))

;; Primes

;; List integers from a to b.
(define (range a b)
  (if (>= a b) nil (cons a (range (+ a 1) b))))

;; Sum elements of s
(define (sum s)
  (reduce + s 0))

;; Is x prime?
(define (prime? x)
  (if (<= x 1) 
      false
      (null? 
       (filter (lambda (y) (= 0 (remainder x y)))
               (range 2 x)))))

;; Sum primes from a to b
(define (sum-primes a b)
  (sum (filter prime? (range a b))))


;; Streams 

(define s (cons-stream 1 (cons-stream 2 nil)))

(define t (cons-stream 1 (/ 1 0)))

(define (range-stream a b)
  (if (>= a b) nil (cons-stream a (range-stream (+ a 1) b))))

;; Infinite Streams

(define (int-stream start)
  (cons-stream start (int-stream (+ start 1))))

(define (prefix s k)
  (if (= k 0) 
      nil 
      (cons (car s) 
            (prefix (cdr-stream s) 
                    (- k 1)))))

;; Processing

(define ones (cons-stream 1 ones))

(define (square-stream s)
  (cons-stream (* (car s) (car s))
               (square-stream (cdr-stream s))))

(define (add-streams s t)
  (cons-stream (+ (car s) (car t))
               (add-streams (cdr-stream s)
                            (cdr-stream t))))

(define ints (cons-stream 1 (add-streams ones ints)))

;; Repeat Example

(define a (cons-stream 1 (cons-stream 2 (cons-stream 3 a))))

(define (f s) (cons-stream (car s) 
                           (cons-stream (car s)
                                        (f (cdr-stream s)))))

(define (g s) (cons-stream (car s)
                           (f (g (cdr-stream s)))))

;; Higher-Order

;; Map f over s.
(define (map-stream f s)
  (if (null? s) 
      nil
      (cons-stream (f (car s))
            (map-stream f 
                 (cdr-stream s)))))
  
;; Filter s by f.
(define (filter-stream f s)
  (if (null? s)
      nil
      (if (f (car s))
          (cons-stream (car s) 
                (filter-stream f (cdr-stream s)))
          (filter-stream f (cdr-stream s)))))

;; Reduce s using f and start value.
(define (reduce-stream f s start)
  (if (null? s) 
      start
      (reduce-stream f
              (cdr-stream s)
              (f start (car s)))))

(define (sum-stream s)
  (reduce-stream + s 0))

(define (sum-primes-stream a b)
  (sum-stream (filter-stream prime? (range-stream a b))))

(define (sieve s)
  (cons-stream 
   (car s) 
   (sieve (filter-stream
           (lambda (x) (< 0 (remainder x (car s))))
           (cdr-stream s)))))

(define primes (sieve (int-stream 2)))

