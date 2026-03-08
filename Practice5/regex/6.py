import re
pattern="[ ,.]"
text=input()
s=re.sub(pattern, ":",text)
print(s)