with open("main.py", "r", encoding="utf-8") as f:
    c = f.read()

target = """    response_headers = {
        "Accept-Ranges": "bytes",
    }"""
replacement = """    response_headers = {
        "Accept-Ranges": "bytes",
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Expose-Headers": "Content-Range, Accept-Ranges, Content-Length",
    }"""

if target in c:
    c = c.replace(target, replacement)
    with open("main.py", "w", encoding="utf-8") as f:
        f.write(c)
        print("Updated CORS headers in proxy")
else:
    print("Not found")
