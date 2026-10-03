from fastapi.testclient import TestClient
from main import app
client = TestClient(app)
response = client.get("/recommend?video_id=AXeB1vrz7II")
print(response.status_code)
print(response.json())
