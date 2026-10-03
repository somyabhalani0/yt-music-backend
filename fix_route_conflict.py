import re
with open("main.py", "r", encoding="utf-8") as f:
    content = f.read()

# 1. Extract import logic from the bottom
import_logic_pattern = r'\nclass PlaylistImport\(BaseModel\):.*'
match = re.search(import_logic_pattern, content, flags=re.DOTALL)
if match:
    extracted_logic = match.group(0)
    content = content.replace(extracted_logic, '\n')
    
    # 2. Insert it ABOVE the @app.get("/playlists/{playlist_id}") or just above @app.post("/playlists")
    target = r'@app\.post\("/playlists"\)'
    content = re.sub(target, extracted_logic.strip() + "\n\n" + '@app.post("/playlists")', content)
    
with open("main.py", "w", encoding="utf-8") as f:
    f.write(content)
