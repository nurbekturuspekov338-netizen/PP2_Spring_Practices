import os

os.makedirs("project/data/raw", exist_ok=True)
os.makedirs("project/data/processed", exist_ok=True)
os.makedirs("project/logs", exist_ok=True)
print("Directory: project")
path="project"
for i in os.listdir(path):
    full_path = os.path.join(path, i)
    if os.path.isfile(full_path):
        print("File: ", i)
    if os.path.isdir(full_path):
        print("Folder:", i)

print("\nDirectory: dir1")    
path="dir1"
for i in os.listdir(path):
    full_path = os.path.join(path, i)
    if os.path.isfile(full_path):
        print("File: ", i)
    if os.path.isdir(full_path):
        print("Folder:", i)