import re
with open("main.py", "r", encoding="utf-8") as f:
    content = f.read()

# Fix duration parsing in get_recommendations
target = "durationSeconds\": track.get('duration_seconds', 0)"
replacement = "durationSeconds\": track.get('duration_seconds', 0) or track.get('duration', 0)"
content = content.replace(target, replacement)

# Wait, yt-dlp duration_string is 'duration_string'
# Let's extract duration properly for related videos
target2 = """            duration = data.get('duration')
            # format duration (seconds to m:ss)"""
# We don't need to change this, it's for playlist import.

with open("main.py", "w", encoding="utf-8") as f:
    f.write(content)
