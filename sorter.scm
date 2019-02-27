(define (insert-sort arr)
  (if (null? arr)
      nil
      (let ((rest (insert-sort (cdr arr))))
        (define (insert val rest)
          (if (or (null? rest)
                  (< val (car rest)))
              (cons val rest)
              (cons (car rest)
                    (insert val (cdr rest)))))
        (insert (car arr) rest))))

(define (merge-sort arr)
  (cond
   ((or (null? arr)
       (null? (cdr arr)))
    nil)
   (let
    ((halves (split arr))))))