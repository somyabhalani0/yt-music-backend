import re
with open('main.py', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace(
"""class UserCreate(BaseModel):
    username: str
    password: str""",
"""class UserCreate(BaseModel):
    username: str
    password: str
    display_name: str | None = None"""
)

# Update register endpoint
content = content.replace(
"""c.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", 
                  (user.username, hash_password(user.password)))""",
"""disp_name = user.display_name or user.username.split('@')[0]
        c.execute("INSERT INTO users (username, password_hash, display_name) VALUES (?, ?, ?)", 
                  (user.username, hash_password(user.password), disp_name))"""
)

# Update get_user_from_token logic or login logic to return display_name
# Wait, login endpoint returns the token. 
# get_user_from_token returns username string? Wait, it returns the username, but maybe I should return a dict?
# Right now frontend just expects currentUser from localstorage.
# The login endpoint returns `{"access_token": token}` and in App.jsx we decode it.
with open('main.py', 'w', encoding='utf-8') as f:
    f.write(content)
