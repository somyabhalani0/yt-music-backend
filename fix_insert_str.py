with open("main.py", "r", encoding="utf-8") as f:
    content = f.read()

target = """                  cursor.execute('''
                      INSERT INTO playlist_tracks (playlist_id, video_id, title, artist, thumbnail, duration, position)
                      VALUES (?, ?, ?, ?, ?, ?, ?)
                  ''', (playlist_id, t["video_id"], t["title"], t["artist"], t["thumbnail"], t["duration"], index))"""

replacement = """                  cursor.execute('''
                      INSERT INTO playlist_tracks (playlist_id, video_id, title, artist, thumbnail, duration)
                      VALUES (?, ?, ?, ?, ?, ?)
                  ''', (playlist_id, t["video_id"], t["title"], t["artist"], t["thumbnail"], t["duration"]))"""

content = content.replace(target, replacement)

with open("main.py", "w", encoding="utf-8") as f:
    f.write(content)
