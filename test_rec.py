from fastapi.testclient import TestClient
from main import app
import json

client = TestClient(app)
response = client.get("/recommend?video_id=s6IqIqIpbRY")
res = response.json()
print("Total recs:", len(res.get("results", [])))
print("First rec duration:", res.get("results", [])[0].get("durationSeconds") if res.get("results") else "No recs")
