f0=open("sample.txt", encoding="utf-8")
data=f0.read()
f0.close()
print(data)

with open("sample.txt", "a") as f:
    f.write("\nuser_id: 101, handle bob@example.com")

f=open("sample.txt", encoding="utf-8")
new=f.read()
print("\n")
print(new)
f.close()