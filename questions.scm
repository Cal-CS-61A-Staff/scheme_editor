((define-macro (apply-twice call-expr)
  (define operator (car call-expr))
  (define operand (car call-expr))
  `(,operator (,operator ,operand))))