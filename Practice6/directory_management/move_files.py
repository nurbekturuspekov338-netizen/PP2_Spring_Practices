import os
import shutil
path="dir1"
path1="project"
for item in os.listdir(path):
    src_path=os.path.join(path, item)
    dst_path=os.path.join(path1, item)
    
    if os.path.exists(dst_path):
        continue
    if os.path.isdir(src_path):
        shutil.copytree(src_path, dst_path)
    else:
        shutil.copy2(src_path, dst_path)