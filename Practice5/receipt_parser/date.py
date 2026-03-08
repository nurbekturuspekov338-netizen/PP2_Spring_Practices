import re

with open("raw.txt", encoding="utf-8") as f:
    text = f.read()

match = re.search(r"Время:\s*(\d{2}\.\d{2}\.\d{4})\s+(\d{2}:\d{2}:\d{2})", text)

if match:
    date = match.group(1)
    time = match.group(2)
    
    print("Дата:", date)
    print("Время:", time)