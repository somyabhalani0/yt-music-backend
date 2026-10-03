with open("main.py", "r", encoding="utf-8") as f:
    lines = f.readlines()

new_lines = []
for line in lines:
    if "INSERT INTO playlist_tracks (playlist_id, video_id, title, artist, thumbnail, duration, position)" in line:
        line = line.replace(", position", "")
    elif "VALUES (?, ?, ?, ?, ?, ?, ?)" in line:
        line = line.replace("?, ?, ?, ?, ?, ?, ?", "?, ?, ?, ?, ?, ?")
    elif "''', (playlist_id, t[\"video_id\"], t[\"title\"], t[\"artist\"], t[\"thumbnail\"], t[\"duration\"], index))" in line:
        line = line.replace(", index)", ")")
    
    new_lines.append(line)

with open("main.py", "w", encoding="utf-8") as f:
    f.writelines(new_lines)
