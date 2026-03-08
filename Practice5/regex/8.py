import re

def split_at_uppercase(text):
    result = re.split(r"(?=[A-Z])", text)
    return result

text = input("Enter string: ")
print(split_at_uppercase(text))