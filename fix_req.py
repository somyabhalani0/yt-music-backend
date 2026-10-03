with open("requirements.txt", "r", encoding="utf-8") as f:
    c = f.read()

c += "\nPyJWT\nbcrypt\n"

with open("requirements.txt", "w", encoding="utf-8") as f:
    f.write(c)
    print("Added dependencies")
