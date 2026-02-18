def square(a, b):
    for i in range(a, b+1):
        yield i*i
        
t=int(input())
v=int(input())

for i in square(t, v):
    print(i)