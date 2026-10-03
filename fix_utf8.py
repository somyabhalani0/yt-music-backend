with open("requirements.txt", "r", encoding="utf-8") as f:
    lines = f.readlines()
lines = list(dict.fromkeys([line.strip() for line in lines if line.strip()]))
with open("requirements.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(lines) + "\n")
