"""
Starting scripts for running all directories all together.

"""
import subprocess

level_names = ["level1", "level2a", "level2b", "level3aa", "level3ab", "level4aba", "level4abb", "level5abba", "level5abbb"]

processes = [subprocess.Popen(["python3", "./run.py", "--level", level_name]) for level_name in level_names]

for p in processes:
    p.wait()

