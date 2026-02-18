def func(N):
    cnt=0
    while N>=cnt:
        if cnt%2==0:
            yield cnt
        cnt+=1

g=int(input())

print(", ".join(str(x) for x in func(g)))