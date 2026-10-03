import re
with open("main.py", "r", encoding="utf-8") as f:
    c = f.read()

target = """@app.get("/proxy-audio")
def proxy_audio(request: Request, url: str):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://www.youtube.com/"
    }
    range_header = request.headers.get('range')
    if range_header:
        headers['Range'] = range_header

    r = requests.get(url, headers=headers, stream=True)

    
    response_headers = {
        "Accept-Ranges": "bytes",
    }
    
    if "content-type" in r.headers:
        response_headers["Content-Type"] = r.headers["content-type"]
    if "content-length" in r.headers:
        response_headers["Content-Length"] = r.headers["content-length"]
    if "content-range" in r.headers:
        response_headers["Content-Range"] = r.headers["content-range"]

    return StreamingResponse(
        r.iter_content(chunk_size=1024 * 64),
        status_code=r.status_code,
        headers=response_headers,
        media_type=r.headers.get("content-type", "audio/mp4")
    )"""

replacement = """import httpx

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
    )"""

if "import httpx" not in c:
    c = c.replace(target, replacement)
    with open("main.py", "w", encoding="utf-8") as f:
        f.write(c)
        print("Updated backend proxy")
else:
    print("Already updated")
