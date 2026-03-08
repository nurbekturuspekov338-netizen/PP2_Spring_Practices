def snake_to_camel(text):
    parts = text.split("_")
    camel = parts[0]
    for word in parts[1:]:
        camel += word.capitalize()
    
    return camel


text = input("Enter snake_case string: ")
print(snake_to_camel(text))