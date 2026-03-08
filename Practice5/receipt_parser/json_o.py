import re
import json

with open("raw.txt", encoding="utf-8") as f:
    text = f.read()


names = re.findall(r"\d+\.\s*\n(.+)", text)

prices = re.findall(r"Стоимость\s+([\d ]+,\d{2})", text)

dt_match = re.search(r"Время:\s*(\d{2}\.\d{2}\.\d{4})\s+(\d{2}:\d{2}:\d{2})", text)
date = dt_match.group(1) if dt_match else None
time = dt_match.group(2) if dt_match else None

method_match = re.search(r"(?m)^\s*([А-Яа-яЁё ]+):\s*$", text)
payment_method = method_match.group(1) if method_match else None

total_match = re.search(r"ИТОГО:\s*([\d ]+,\d{2})", text)
total = total_match.group(1) if total_match else None

data = {
    "date": date,
    "time": time,
    "payment_method": payment_method,
    "total": total,
    "items": []
}

for name, price in zip(names, prices):
    data["items"].append({
        "name": name,
        "price": price
    })

print(json.dumps(data, ensure_ascii=False, indent=4))