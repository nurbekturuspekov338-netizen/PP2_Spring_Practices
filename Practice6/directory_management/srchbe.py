import os
path="dir1"
for roots, dirs, files in os.walk(path):
    for file in files:
        if file.endswith("txt"):
            print(os.path.join(roots, file))