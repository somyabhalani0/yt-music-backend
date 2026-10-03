import subprocess
import json
from pydantic import BaseModel

def parse_duration(d):
    if isinstance(d, int): return d
    if not d: return 0
    parts = str(d).split(':')
    try:
        if len(parts) == 3:
            return int(parts[0])*3600 + int(parts[1])*60 + int(parts[2])
        elif len(parts) == 2:
            return int(parts[0])*60 + int(parts[1])
        return int(parts[0])
    except:
        return 0

from fastapi import HTTPException, Depends

def parse_duration(d):
    if isinstance(d, int): return d
    if not d: return 0
    parts = str(d).split(':')
    try:
        if len(parts) == 3:
            return int(parts[0])*3600 + int(parts[1])*60 + int(parts[2])
        elif len(parts) == 2:
            return int(parts[0])*60 + int(parts[1])
        return int(parts[0])
    except:
        return 0

from fastapi import FastAPI, Response, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from ytmusicapi import YTMusic
import yt_dlp
import uvicorn
import requests

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/proxy-image")
def proxy_image(url: str):
    try:
        r = requests.get(url)
        return Response(content=r.content, media_type=r.headers.get("content-type", "image/jpeg"))
    except Exception as e:
        return {"error": str(e)}

import httpx

@app.get("/proxy-audio")
async def proxy_audio(request: Request, url: str):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://www.youtube.com/"
    }
    range_header = request.headers.get('range')
    if range_header:
        headers['Range'] = range_header

    client = httpx.AsyncClient()
    req = client.build_request("GET", url, headers=headers)
    r = await client.send(req, stream=True, follow_redirects=True)
    
    response_headers = {
        "Accept-Ranges": "bytes",
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Expose-Headers": "Content-Range, Accept-Ranges, Content-Length",
    }
    
    if "content-type" in r.headers:
        response_headers["Content-Type"] = r.headers["content-type"]
    if "content-length" in r.headers:
        response_headers["Content-Length"] = r.headers["content-length"]
    if "content-range" in r.headers:
        response_headers["Content-Range"] = r.headers["content-range"]

    async def stream_generator():
        try:
            async for chunk in r.aiter_bytes(chunk_size=1024 * 64):
                if chunk:
                    yield chunk
        except Exception as e:
            print("Streaming error:", e)
        finally:
            await r.aclose()
            await client.aclose()

    return StreamingResponse(
        stream_generator(),
        status_code=r.status_code,
        headers=response_headers,
        media_type=r.headers.get("content-type", "audio/mp4")
    )

ytmusic = YTMusic()

ydl_opts = {
    'format': 'bestaudio[ext=m4a]/bestaudio/best',
    'quiet': True,
    'no_warnings': True,
    'extract_flat': True,
    'skip_download': True
}
ydl = yt_dlp.YoutubeDL(ydl_opts)


@app.get("/search")
def search(q: str):
    try:
        # Search both songs and videos to get a full list of results
        songs = ytmusic.search(q, filter="songs", limit=20)
        videos = ytmusic.search(q, filter="videos", limit=20)
        
        # Combine and interleave them slightly
        results = []
        for i in range(max(len(songs), len(videos))):
            if i < len(songs): results.append(songs[i])
            if i < len(videos): results.append(videos[i])
            
        mapped = []
        for item in results:
                
            # Get highest quality thumbnail
            thumbnails = item.get('thumbnails', [])
            thumbnail_url = thumbnails[-1]['url'] if thumbnails else ""
            
            if "=" in thumbnail_url:
                thumbnail_url = thumbnail_url.split("=")[0] + "=w800-h800-l90-rj"
            
            # Extract artists
            artists = ", ".join([a['name'] for a in item.get('artists', [])])
            
            mapped.append({
                "id": item['videoId'],
                "title": item['title'],
                "uploaderName": artists,
                "thumbnail": thumbnail_url,
                "durationSeconds": item.get('duration_seconds', 0),
                "type": item.get('resultType')
            })
            
        return {"results": mapped}
    except Exception as e:
        return {"error": str(e)}

@app.get("/recommend")
def recommend(video_id: str):
    try:
        # Some video IDs fail with get_watch_playlist if they are not music.
        # If it fails, fallback to a generic search for recommendations.
        try:
            playlist = ytmusic.get_watch_playlist(videoId=video_id, limit=20)
        except Exception:
            # Fallback
            return {"results": []}
        tracks = playlist.get('tracks', [])
        mapped = []
        for item in tracks:
            if item['videoId'] == video_id:
                continue
                
            thumbnails = item.get('thumbnail', [])
            thumbnail_url = thumbnails[-1]['url'] if thumbnails else ""
            if "=" in thumbnail_url:
                thumbnail_url = thumbnail_url.split("=")[0] + "=w800-h800-l90-rj"
            
            artists = ", ".join([a['name'] for a in item.get('artists', [])])
            mapped.append({
                "id": item['videoId'],
                "title": item['title'],
                "uploaderName": artists,
                "thumbnail": thumbnail_url,
                "durationSeconds": parse_duration(item.get('duration_seconds', 0) or item.get('length', 0) or 0),
                "type": "song"
            })
        return {"results": mapped}
    except Exception as e:
        return {"error": str(e)}

@app.get("/stream/{video_id}")
def get_stream(video_id: str):
    try:
        # Extract real audio stream URL using yt-dlp without downloading
        info = ydl.extract_info(f"https://www.youtube.com/watch?v={video_id}", download=False)
        
        # Get the best audio-only format
        formats = info.get('formats', [])
        audio_formats = [f for f in formats if f.get('acodec') != 'none' and f.get('vcodec') == 'none']
        
        if not audio_formats:
            return {"error": "No audio formats found"}
            
        # Sort by quality (usually higher bitrates are better)
        best_audio = sorted(audio_formats, key=lambda f: f.get('abr', 0) or 0, reverse=True)[0]
        
        return {
            "streamUrl": best_audio['url'],
            "duration": info.get('duration')
        }
    except Exception as e:
        return {"error": str(e)}


@app.get("/playlist")
def get_playlist(playlist_id: str):
    try:
        playlist = ytmusic.get_playlist(playlist_id, limit=100)
        mapped = []
        for track in playlist.get('tracks', []):
            if not track.get('videoId'):
                continue
            thumbnails = track.get('thumbnails', [])
            thumbnail_url = thumbnails[-1]['url'] if thumbnails else ""
            if "=" in thumbnail_url:
                thumbnail_url = thumbnail_url.split("=")[0] + "=w800-h800-l90-rj"
                
            artists = ", ".join([a['name'] for a in track.get('artists', []) if 'name' in a])
            
            mapped.append({
                "id": track['videoId'],
                "title": track['title'],
                "uploaderName": artists,
                "thumbnail": thumbnail_url,
                "durationSeconds": track.get('duration_seconds', 0) or track.get('duration', 0)
            })
        return {"results": mapped}
    except Exception as e:
        return {"error": str(e)}





from db import init_db, get_db, hash_password, verify_password, create_access_token, get_current_user_id, db_lock

def parse_duration(d):
    if isinstance(d, int): return d
    if not d: return 0
    parts = str(d).split(':')
    try:
        if len(parts) == 3:
            return int(parts[0])*3600 + int(parts[1])*60 + int(parts[2])
        elif len(parts) == 2:
            return int(parts[0])*60 + int(parts[1])
        return int(parts[0])
    except:
        return 0

from fastapi import HTTPException, Depends, Header
from pydantic import BaseModel
from typing import Optional

# Run init_db on startup
init_db()

class UserCreate(BaseModel):
    username: str
    password: str
    display_name: str | None = None

class PlaylistCreate(BaseModel):
    name: str

class TrackAdd(BaseModel):
    video_id: str
    title: str
    artist: str
    thumbnail: str
    duration: str | int = 0

def get_user_from_token(authorization: Optional[str] = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Unauthorized")
    token = authorization.split(" ")[1]
    user_id = get_current_user_id(token)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")
    return user_id

@app.post("/auth/register")
def register(user: UserCreate):
    with db_lock:
        conn = get_db()
        c = conn.cursor()
        c.execute("SELECT id FROM users WHERE username = ?", (user.username,))
        if c.fetchone():
            return {"error": "Username already taken"}
        disp_name = user.display_name or user.username.split('@')[0]
        c.execute("INSERT INTO users (username, password_hash, display_name) VALUES (?, ?, ?)", 
                  (user.username, hash_password(user.password), disp_name))
        user_id = c.lastrowid
        conn.commit()
        conn.close()
    
    token = create_access_token({"sub": str(user_id), "username": user.username, "display_name": disp_name})
    return {"token": token, "username": user.username, "display_name": disp_name}

@app.post("/auth/login")
def login(user: UserCreate):
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT id, username, password_hash, display_name FROM users WHERE username = ?", (user.username,))
    row = c.fetchone()
    conn.close()
    
    if not row or not verify_password(user.password, row["password_hash"]):
        return {"error": "Invalid credentials"}
        
    disp_name = row["display_name"] or row["username"].split('@')[0]
    token = create_access_token({"sub": str(row["id"]), "username": row["username"], "display_name": disp_name})
    return {"token": token, "username": row["username"], "display_name": disp_name}

@app.get("/playlists/me")
def get_my_playlists(user_id: int = Depends(get_user_from_token)):
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT id, name, created_at FROM playlists WHERE user_id = ? ORDER BY created_at DESC", (user_id,))
    playlists = [dict(row) for row in c.fetchall()]
    conn.close()
    return {"playlists": playlists}

class PlaylistImport(BaseModel):
    url: str

@app.post("/playlists/import")
def import_playlist(req: PlaylistImport, user_id: int = Depends(get_user_from_token)):
    print(f"Importing playlist: {req.url} for user: {user_id}")
    try:
        # Run yt-dlp to extract flat playlist
        import sys
        cmd = [sys.executable, "-m", "yt_dlp", "--dump-json", "--flat-playlist", req.url]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        
        lines = result.stdout.strip().split('\n')
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
                
                title = data.get('title') or 'Unknown Title'
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
                    INSERT INTO playlist_tracks (playlist_id, video_id, title, artist, thumbnail, duration)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (playlist_id, t["video_id"], t["title"], t["artist"], t["thumbnail"], t["duration"]))
            
            db.commit()
            
        return {"id": playlist_id, "name": playlist_title, "track_count": len(tracks)}
        
    except subprocess.CalledProcessError as e:
        print(e.stderr)
        raise HTTPException(status_code=400, detail="Failed to fetch playlist. Ensure URL is valid and public.")

@app.post("/playlists")
def create_playlist(playlist: PlaylistCreate, user_id: int = Depends(get_user_from_token)):
    with db_lock:
        conn = get_db()
        c = conn.cursor()
        c.execute("INSERT INTO playlists (user_id, name) VALUES (?, ?)", (user_id, playlist.name))
        pid = c.lastrowid
        conn.commit()
        conn.close()
    return {"id": pid, "name": playlist.name}

@app.post("/playlists/{playlist_id}/tracks")
def add_track(playlist_id: int, track: TrackAdd, user_id: int = Depends(get_user_from_token)):
    with db_lock:
        conn = get_db()
        c = conn.cursor()
        c.execute("SELECT id FROM playlists WHERE id = ? AND user_id = ?", (playlist_id, user_id))
        if not c.fetchone():
            return {"error": "Playlist not found or unauthorized"}
            
        c.execute("""
            INSERT INTO playlist_tracks (playlist_id, video_id, title, artist, thumbnail, duration)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (playlist_id, track.video_id, track.title, track.artist, track.thumbnail, track.duration))
        conn.commit()
        conn.close()
    return {"success": True}

@app.get("/playlists/{playlist_id}")
def get_playlist_tracks(playlist_id: int, user_id: int = Depends(get_user_from_token)):
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT name FROM playlists WHERE id = ? AND user_id = ?", (playlist_id, user_id))
    row = c.fetchone()
    if not row:
        return {"error": "Playlist not found or unauthorized"}
    
    c.execute("""
        SELECT video_id as id, title, artist as uploaderName, thumbnail, duration as durationSeconds 
        FROM playlist_tracks WHERE playlist_id = ? ORDER BY added_at ASC
    """, (playlist_id,))
    tracks = [dict(r) for r in c.fetchall()]
    conn.close()
    return {"name": row["name"], "tracks": tracks}

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 3001))
    uvicorn.run(app, host='0.0.0.0', port=port)




@app.post("/playlists/import-no-db")
def import_playlist_no_db(req: PlaylistImport):
    try:
        import sys, subprocess, json
        cmd = [sys.executable, "-m", "yt_dlp", "--dump-json", "--flat-playlist", req.url]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        
        lines = result.stdout.strip().split('\n')
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
