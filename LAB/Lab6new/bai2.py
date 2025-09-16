
import json
from kanren import Relation, facts, run, conde, var


# Định nghĩa quan hệ
father = Relation()
mother = Relation()


# Load dữ liệu
with open('relationships.json', encoding="utf-8") as f: 
    d = json.load(f)


for item in d['father']:
    facts(father, (list(item.keys())[0], list(item.values())[0]))


for item in d['mother']:
    facts(mother, (list(item.keys())[0], list(item.values())[0]))


# Định nghĩa quan hệ suy diễn
def parent(x, y):
    return conde([father(x, y)], [mother(x, y)])


def grandparent(x, y):
    temp = var()
    return conde((parent(x, temp), parent(temp, y)))


def sibling(x, y):
    temp = var()
    return conde((parent(temp, x), parent(temp, y)))


def uncle(x, y):
    temp = var()
    return conde((father(temp, x), grandparent(temp, y)))



x = var()
print("Children of John:", run(0, x, father("John", x)))
print("Adam’s parents:", run(0, x, parent(x, "Adam")))
print("Wayne’s grandparents:", run(0, x, grandparent(x, "Wayne")))
print("David’s siblings:", run(0, x, sibling(x, "David")))
print("Tiffany’s uncles:", run(0, x, uncle(x, "Tiffany")))
