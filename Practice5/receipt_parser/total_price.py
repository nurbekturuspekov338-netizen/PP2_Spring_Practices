import re

with open("raw.txt", encoding="utf-8") as f:
    text = f.read()

total_sum = re.search(r"ИТОГО:\s*([\d ]+,\d{2})", text)

if total_sum:
    print(total_sum.group(1))