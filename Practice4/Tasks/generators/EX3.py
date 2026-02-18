def func(N):
    for i in range(12, N+1, 12):
        yield i

n = int(input())

for i in func(n):
    print(i)
