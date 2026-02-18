def fun(а):
    cnt = 1
    while cnt <= а:
        yield cnt*cnt
        cnt += 1

j=int(input())
ctr = fun(j)
for n in ctr:
    print(n)
