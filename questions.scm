(define-macro (let-macro bindings body)
  `((lambda ,(map car bindings) ,body)
    ,@(map cadr bindings)))

(let ((a (let ((a 5))
           a))
      (b 2)
      (c 3))
  (* a b c))