with open("main.py", "r", encoding="utf-8") as f:
    content = f.read()

content = "import subprocess\nimport json\n" + content

with open("main.py", "w", encoding="utf-8") as f:
    f.write(content)
