import re 

def text_to_match(text):
    pattern = r"\b[a-z]+(?:_[a-z]+)+\b"
    
    matches = re.findall(pattern, text)
    
    if matches:
        return "Found words: " + ", ".join(matches)
    else:
        return "No match found!"

text = input()
print(text_to_match(text))