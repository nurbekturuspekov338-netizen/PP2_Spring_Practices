import re

text = "hello_world test_var abc test_123 wrong_Var good_example_name"

pattern = r"\b[a-z]+(?:_[a-z]+)+\b"

matches = re.findall(pattern, text)

print(matches)