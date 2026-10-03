with open("main.py", "r", encoding="utf-8") as f:
    content = f.read()

target = "title = data.get('title', 'Unknown Title')"
replacement = "title = data.get('title') or 'Unknown Title'"

content = content.replace(target, replacement)

with open("main.py", "w", encoding="utf-8") as f:
    f.write(content)
