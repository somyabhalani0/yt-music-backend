with open("main.py", "r", encoding="utf-8") as f:
    content = f.read()

content = content.replace("split('\n')", "split('\\n')")

with open("main.py", "w", encoding="utf-8") as f:
    f.write(content)
