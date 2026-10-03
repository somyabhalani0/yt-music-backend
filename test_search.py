from fastapi.testclient import TestClient
from main import app
import json

client = TestClient(app)
response = client.get("/search?q=sharmeeli")
res = response.json()
print("Total results:", len(res.get("results", [])))
print("First 3:", res.get("results", [])[:3])
