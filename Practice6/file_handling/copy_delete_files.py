import shutil
import os 
shutil.copy("sample.txt", "copy.txt")
shutil.copy2("sample.txt", "copy_with_metadata.txt")
os.makedirs("Tree", exist_ok=True)
shutil.copy2("sample.txt", "Tree/data_backup.txt")
os.remove("sample.txt")
