import re

with open("main.py", "r", encoding="utf-8") as f:
    c = f.read()

helper = """
def parse_duration(d):
    if isinstance(d, int): return d
    if not d: return 0
    parts = str(d).split(':')
    try:
        if len(parts) == 3:
            return int(parts[0])*3600 + int(parts[1])*60 + int(parts[2])
        elif len(parts) == 2:
            return int(parts[0])*60 + int(parts[1])
        return int(parts[0])
    except:
        return 0
"""

if "def parse_duration" not in c:
    c = c.replace("from fastapi import", helper + "\nfrom fastapi import")

old_rec_duration = '''"durationSeconds": item.get('duration_seconds', 0) or item.get('length', 0) or 0,'''
new_rec_duration = '''"durationSeconds": parse_duration(item.get('duration_seconds', 0) or item.get('length', 0) or 0),'''
c = c.replace(old_rec_duration, new_rec_duration)

with open("main.py", "w", encoding="utf-8") as f:
    f.write(c)
    print("Fixed duration parsing in backend")
