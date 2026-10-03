import re
with open("main.py", "r", encoding="utf-8") as f:
    content = f.read()

target = r'token = create_access_token\(\{"sub": str\(user_id\), "username": user.username\}\)\s+return \{"token": token, "username": user.username\}'
replacement = 'token = create_access_token({"sub": str(user_id), "username": user.username, "display_name": disp_name})\n    return {"token": token, "username": user.username, "display_name": disp_name}'

new_content = re.sub(target, replacement, content)
with open("main.py", "w", encoding="utf-8") as f:
    f.write(new_content)
