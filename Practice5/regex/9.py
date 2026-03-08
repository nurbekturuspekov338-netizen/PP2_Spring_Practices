import re

def insert_spaces(text):
    result = re.sub(r"(?<!^)(?=[A-Z])", " ", text)
    return result

text = input("Enter string: ")
print(insert_spaces(text))