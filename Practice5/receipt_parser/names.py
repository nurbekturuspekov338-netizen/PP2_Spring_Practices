import re

with open("raw.txt", encoding="utf-8") as f:
    text = f.read()

names = re.findall(r"\d+\.\s*\n(.+)", text)

for name in names:
    print(f"Название: {name}")