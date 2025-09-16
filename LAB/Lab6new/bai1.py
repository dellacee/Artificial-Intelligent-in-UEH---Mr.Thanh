from kanren import run, var, fact
import kanren.assoccomm as la


# Khai báo phép toán
add = 'addition'
mul = 'multiplication'


# Khai báo tính chất giao hoán & kết hợp
fact(la.commutative, add)
fact(la.commutative, mul)
fact(la.associative, add)
fact(la.associative, mul)


# Biến
a, b, c = var(), var(), var()


# Biểu thức gốc: 3 * (-2) + (1 + 2*3) * (-1)
expression_orig = (add, (mul, 3, -2), (mul, (add, 1, (mul, 2, 3)), -1))


# Các biểu thức cần so khớp
expression1 = (add, (mul, (add, 1, (mul, 2, a)), b), (mul, 3, c))
expression2 = (add, (mul, c, 3), (mul, b, (add, (mul, 2, a), 1)))
expression3 = (add, (add, (mul, (mul, 2, a), b), b), (mul, 3, c))


# So khớp
print(run(0, (a, b, c), la.eq_assoccomm(expression1, expression_orig)))
print(run(0, (a, b, c), la.eq_assoccomm(expression2, expression_orig)))
print(run(0, (a, b, c), la.eq_assoccomm(expression3, expression_orig)))