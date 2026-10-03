with open("main.py", "r", encoding="utf-8") as f:
    c = f.read()

c = c.replace("uvicorn.run(app, host='0.0.0.0', port=3001)", "import os\n    port = int(os.environ.get('PORT', 3001))\n    uvicorn.run(app, host='0.0.0.0', port=port)")

with open("main.py", "w", encoding="utf-8") as f:
    f.write(c)
    print("Fixed PORT for deployment")
