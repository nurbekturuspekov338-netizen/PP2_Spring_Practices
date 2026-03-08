import re
with open("raw.txt", encoding="utf-8") as f:
    text=f.read()
method=re.search(r"(?m)^\s*([А-Яа-яЁё ]+):\s*$", text)
if method:
    m = method.group(1).strip()
    print("Метод оплаты:", method)
else:
    print("Метод оплаты не найден")