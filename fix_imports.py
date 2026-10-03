with open("main.py", "r", encoding="utf-8") as f:
    content = f.read()

content = "from pydantic import BaseModel\nfrom fastapi import HTTPException, Depends\n" + content

with open("main.py", "w", encoding="utf-8") as f:
    f.write(content)
