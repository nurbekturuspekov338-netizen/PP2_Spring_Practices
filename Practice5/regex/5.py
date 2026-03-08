import re
pattern=r"^a.*b$"
text=input()
mat=re.match(pattern, text)
if mat:
    print("Match")
else:
    print("No match")