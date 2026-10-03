import re

with open("main.py", "r", encoding="utf-8") as f:
    content = f.read()

target = r'cmd = \["yt-dlp", "--dump-json", "--flat-playlist", req\.url\]'
replacement = r'import sys\n        cmd = [sys.executable, "-m", "yt_dlp", "--dump-json", "--flat-playlist", req.url]'

content = re.sub(target, replacement, content)

with open("main.py", "w", encoding="utf-8") as f:
    f.write(content)
