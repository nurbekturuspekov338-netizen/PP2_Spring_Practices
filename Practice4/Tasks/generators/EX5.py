def func(N):
    cnt=0
    while N>=cnt:
        yield N
        N=N-1
        
n=int(input())
for i in func(n):
    print(i)