import re
with open("main.py", "r", encoding="utf-8") as f:
    content = f.read()

# Remove the import logic from the middle
import_logic_pattern = r'\nclass PlaylistImport\(BaseModel\):.*?(?=@app\.get\("/search"\))'
match = re.search(import_logic_pattern, content, flags=re.DOTALL)
if match:
    extracted_logic = match.group(0)
    content = content.replace(extracted_logic, '\n')
    # Append it to the bottom
    content += "\n" + extracted_logic
    
with open("main.py", "w", encoding="utf-8") as f:
    f.write(content)
