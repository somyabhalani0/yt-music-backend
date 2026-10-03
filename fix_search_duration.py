with open("main.py", "r", encoding="utf-8") as f:
    c = f.read()

old = """"durationSeconds": item.get('duration_seconds', 0),"""
new = """"durationSeconds": parse_duration(item.get('duration_seconds', 0) or item.get('duration', 0) or item.get('length', 0) or 0),"""

c = c.replace(old, new)

with open("main.py", "w", encoding="utf-8") as f:
    f.write(c)
    print("Fixed duration in search")
