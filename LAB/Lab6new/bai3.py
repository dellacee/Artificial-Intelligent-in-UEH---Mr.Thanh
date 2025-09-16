from kanren import run, var, membero, eq
from kanren.core import lall


# Biến
people = var()


# Tập luật
rules = lall(
    (eq, (var(), var(), var(), var()), people),
    (membero, ('Steve', var(), 'blue', var()), people),
    (membero, (var(), 'cat', var(), 'Canada'), people),
    (membero, ('Matthew', var(), var(), 'USA'), people),
    (membero, (var(), var(), 'black', 'Australia'), people),
    (membero, ('Jack', 'cat', var(), var()), people),
    (membero, ('Alfred', var(), var(), 'Australia'), people),
    (membero, (var(), 'dog', var(), 'France'), people),
    (membero, (var(), 'rabbit', var(), var()), people)   # tìm người nuôi rabbit
)


# Giải
solutions = run(0, people, rules)


# Kết quả
output = [house for house in solutions[0] if 'rabbit' in house][0][0]
print(output, "is the owner of the rabbit")
print("\nHere are all the details:")
for item in solutions[0]:
    print(item)


