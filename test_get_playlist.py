import requests
import jwt
from datetime import datetime, timedelta

SECRET_KEY = "super-secret-local-key"
ALGORITHM = "HS256"

def create_token(user_id):
    to_encode = {"sub": str(user_id), "exp": datetime.utcnow() + timedelta(minutes=60)}
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

token = create_token(1)

res = requests.get(
    "http://localhost:3001/playlists/1",
    headers={"Authorization": "Bearer " + token}
)
print("STATUS", res.status_code)
print(res.text)
