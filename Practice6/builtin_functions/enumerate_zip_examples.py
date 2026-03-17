fruits = ["яблоко", "груша", "банан", "киви", "апельсин"]
prices = [180, 220, 140, 320, 250]
weights = [0.3, 0.25, 0.18, 0.09, 0.4]

for i, fruit in enumerate(fruits, 1):
    print(f"{i:2}. {fruit}")


for fruit, price in zip(fruits, prices):
    print(f"{fruit:10} — {price} тг/кг")


for idx, (fruit, price, weight) in enumerate(zip(fruits, prices, weights), 1):
    cost_per_kg = round(price / weight, 1) if weight > 0 else 0
    print(f"{idx}. {fruit:10} — {price} тг  ({weight} кг) → {cost_per_kg} тг/кг")