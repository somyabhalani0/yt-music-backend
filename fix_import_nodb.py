import re

with open("main.py", "r", encoding="utf-8") as f:
    c = f.read()

new_endpoint = """
@app.post("/playlists/import-no-db")
def import_playlist_no_db(req: PlaylistImport):
    try:
        import sys, subprocess, json
        cmd = [sys.executable, "-m", "yt_dlp", "--dump-json", "--flat-playlist", req.url]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        
        lines = result.stdout.strip().split('\\n')
        if not lines or not lines[0]:
            raise HTTPException(status_code=400, detail="Could not parse playlist")
        
        playlist_title = "Imported Playlist"
        tracks = []
        for line in lines:
            try:
                data = json.loads(line)
                if data.get('playlist_title'):
                    playlist_title = data.get('playlist_title')
                vid = data.get('id')
                if not vid:
                    continue
                tracks.append({
                    "id": vid,
                    "title": data.get('title', 'Unknown'),
                    "artist": data.get('uploader', 'Unknown'),
                    "thumbnail": f"https://i.ytimg.com/vi/{vid}/hqdefault.jpg"
                })
            except:
                pass
        return {"title": playlist_title, "tracks": tracks}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
"""

if "import-no-db" not in c:
    c = c + "\n" + new_endpoint
    with open("main.py", "w", encoding="utf-8") as f:
        f.write(c)
        print("Backend No-DB import added")
else:
    print("Already added")
