import random
random.seed(5)
print(random.random())
print(random.random())

import random
r1 = random.randint(5, 15)
print(r1)

r2 = random.randint(-10, -2)
print(r2)

import random

a = [1, 2, 3, 4, 5, 6]
print(random.choice(a))

s = "geeks"
print(random.choice(s))

tup = (1, 2, 3, 4, 5)
print(random.choice(tup))

import random
a = [1, 2, 3, 4, 5]

random.shuffle(a)
print("After shuffle : ")
print(a)

random.shuffle(a)
print("\nSecond shuffle : ")
print(a)