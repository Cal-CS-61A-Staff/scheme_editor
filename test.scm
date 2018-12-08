(if (null? lst)
    nil
    (cons (func (car lst))
    (map func (cdr lst)))))