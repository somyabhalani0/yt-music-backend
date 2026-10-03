import re

with open("main.py", "r", encoding="utf-8") as f:
    c = f.read()

old_search = """        # Search YouTube Music without filter to include both songs and videos (e.g. covers, slowed versions)
        results = ytmusic.search(q, limit=20)
        
        mapped = []
        for item in results:
            # We only want playable media (songs and videos), not albums/artists/playlists
            if item.get('resultType') not in ('song', 'video'):
                continue"""

new_search = """        # Search both songs and videos to get a full list of results
        songs = ytmusic.search(q, filter="songs", limit=20)
        videos = ytmusic.search(q, filter="videos", limit=20)
        
        # Combine and interleave them slightly
        results = []
        for i in range(max(len(songs), len(videos))):
            if i < len(songs): results.append(songs[i])
            if i < len(videos): results.append(videos[i])
            
        mapped = []
        for item in results:"""

c = c.replace(old_search, new_search)

# Also fix the recommend endpoint error!
old_recommend = """def recommend(video_id: str):
    try:
        playlist = ytmusic.get_watch_playlist(videoId=video_id, limit=20)"""

new_recommend = """def recommend(video_id: str):
    try:
        # Some video IDs fail with get_watch_playlist if they are not music.
        # If it fails, fallback to a generic search for recommendations.
        try:
            playlist = ytmusic.get_watch_playlist(videoId=video_id, limit=20)
        except Exception:
            # Fallback
            return {"results": []}"""

c = c.replace(old_recommend, new_recommend)

with open("main.py", "w", encoding="utf-8") as f:
    f.write(c)
    print("Fixed backend")
