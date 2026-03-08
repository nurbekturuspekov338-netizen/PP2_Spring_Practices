import re

pattern = r"^ab*$"

tstr=input()

d=re.fullmatch(pattern, tstr)
if d:
    print("MATCH")
else:
    print("NO MATCH")
