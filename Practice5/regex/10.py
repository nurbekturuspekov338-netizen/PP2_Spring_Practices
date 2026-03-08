import re

def camel_to_snake(text):
    snake = re.sub(r'(?<!^)(?=[A-Z])', '_', text)
    return snake.lower()

text = input("Enter camelCase string: ")
print(camel_to_snake(text))