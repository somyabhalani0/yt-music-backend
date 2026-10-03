import re
with open('main.py', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace(
"""c.execute("SELECT id, username, password_hash FROM users WHERE username = ?", (user.username,))""",
"""c.execute("SELECT id, username, password_hash, display_name FROM users WHERE username = ?", (user.username,))"""
)

content = content.replace(
"""token = create_access_token({"sub": str(row["id"]), "username": row["username"]})
    return {"token": token, "username": row["username"]}""",
"""disp_name = row["display_name"] or row["username"].split('@')[0]
    token = create_access_token({"sub": str(row["id"]), "username": row["username"], "display_name": disp_name})
    return {"token": token, "username": row["username"], "display_name": disp_name}"""
)

# And in register we can return display_name too:
content = content.replace(
"""token = create_access_token({"sub": str(new_id), "username": user.username})
        return {"token": token, "username": user.username}""",
"""token = create_access_token({"sub": str(new_id), "username": user.username, "display_name": disp_name})
        return {"token": token, "username": user.username, "display_name": disp_name}"""
)

with open('main.py', 'w', encoding='utf-8') as f:
    f.write(content)
