import re
with open("raw.txt", encoding="utf-8") as f:
    data=f.read()

price= re.findall(r"Стоимость\s+([\d ]+,\d{2})", data)
print(price)