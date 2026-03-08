import re

pattern = r"^ab{2,3}$"

test_strings = ["abb", "abbb", "abbbb", "ab", "a", "abbc"]

for s in test_strings:
    if re.fullmatch(pattern, s):
        print(f"{s} → MATCH")
    else:
        print(f"{s} → NO MATCH")