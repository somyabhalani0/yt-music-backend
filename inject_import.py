import json
import re
import subprocess

with open("main.py", "r", encoding="utf-8") as f:
    content = f.read()

import_logic = """
class PlaylistImport(BaseModel):
    url: str

@app.post("/playlists/import")
def import_playlist(req: PlaylistImport, user_id: int = Depends(get_user_from_token)):
    print(f"Importing playlist: {req.url} for user: {user_id}")
    try:
        # Run yt-dlp to extract flat playlist
        cmd = ["yt-dlp", "--dump-json", "--flat-playlist", req.url]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        
        lines = result.stdout.strip().split('\\n')
        if not lines or not lines[0]:
            raise HTTPException(status_code=400, detail="Could not parse playlist")
        
        # The playlist title can usually be found in the first track's playlist_title field
        # or we just name it "Imported Playlist" if not found
        playlist_title = "Imported Playlist"
        tracks = []
        for line in lines:
            try:
                data = json.loads(line)
                if data.get('playlist_title'):
                    playlist_title = data.get('playlist_title')
                
                # yt-dlp flat-playlist format
                vid = data.get('id')
                if not vid:
                    continue
                
                title = data.get('title', 'Unknown Title')
                artist = data.get('uploader') or data.get('channel') or 'Unknown Artist'
                
                thumbnails = data.get('thumbnails', [])
                thumbnail = thumbnails[-1]['url'] if thumbnails else ''
                
                duration = data.get('duration')
                # format duration (seconds to m:ss)
                if duration:
                    m = int(duration // 60)
                    s = int(duration % 60)
                    dur_str = f"{m}:{s:02d}"
                else:
                    dur_str = "0:00"
                
                tracks.append({
                    "video_id": vid,
                    "title": title,
                    "artist": artist,
                    "thumbnail": thumbnail,
                    "duration": dur_str
                })
            except Exception as e:
                print("Error parsing track line:", e)
                
        if not tracks:
            raise HTTPException(status_code=400, detail="No tracks found in playlist")
            
        with get_db() as db:
            cursor = db.cursor()
            cursor.execute("INSERT INTO playlists (user_id, name) VALUES (?, ?)", (user_id, playlist_title))
            playlist_id = cursor.lastrowid
            
            for index, t in enumerate(tracks):
                cursor.execute('''
                    INSERT INTO playlist_tracks (playlist_id, video_id, title, artist, thumbnail, duration, position)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (playlist_id, t["video_id"], t["title"], t["artist"], t["thumbnail"], t["duration"], index))
            
            db.commit()
            
        return {"id": playlist_id, "name": playlist_title, "track_count": len(tracks)}
        
    except subprocess.CalledProcessError as e:
        print(e.stderr)
        raise HTTPException(status_code=400, detail="Failed to fetch playlist. Ensure URL is valid and public.")
"""

if "/playlists/import" not in content:
    content = content.replace("@app.get(\"/search\")", import_logic + "\n@app.get(\"/search\")")
    with open("main.py", "w", encoding="utf-8") as f:
        f.write(content)
        
