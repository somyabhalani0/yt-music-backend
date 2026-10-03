import requests

res = requests.post(
    "http://localhost:3001/playlists/import",
    headers={"Authorization": "Bearer " + "YOUR_TOKEN_HERE"}, # we need a token
    json={"url": "https://youtube.com/playlist?list=PLYGC49-2XzcI8jjgXcV2UQmijzGrZO_gv"}
)
print(res.status_code)
print(res.text)
