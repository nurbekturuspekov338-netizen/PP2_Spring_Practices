#readline method only read one line
#readlines read all lines and keep safe them in list format
with open("sample.txt", encoding="utf-8") as f:
    data1=f.readline()
    data2=f.readlines()

print(data1)
print(data2)

with open("sample.txt", encoding="utf-8") as f:
    data=f.read(10)
    data3=f.read(10)
    data4=f.read()

print(data)
print(data3)
print(data4)    