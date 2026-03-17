from functools import reduce
numbers = [3, 12, 7, 8, 15, 4, 9, 2, 11, 6]


doubled = list(map(lambda x: x * 2, numbers))
print(doubled)

big_numbers = list(filter(lambda x: x > 7, numbers))
print(big_numbers)

squares_of_multiples_of_3 = list(map(lambda x: x**2, filter(lambda x: x % 3 == 0, numbers)))
print(squares_of_multiples_of_3)

sum_all = reduce(lambda x, y: x + y, numbers)
print(sum_all)

product = reduce(lambda x, y: x * y, numbers, 1)  
print(product)

minimum = reduce(lambda x, y: x if x < y else y, numbers)
print(minimum)
