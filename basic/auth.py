from fastapi import FastAPI, Request, HTTPException, status, Depends
from base64 import b64decode
import uvicorn

app = FastAPI()

USERS = {
    "admin": "admin",
    "tan": "Pass123"
}

def basic_auth(request: Request):
    auth = request.headers.get("Authorization")

    if not auth:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    try:
        encoded_credentials = auth.split(" ")[1]
        decoded_bytes = b64decode(encoded_credentials)
        decoded_str = decoded_bytes.decode("utf-8")
        username, password = decoded_str.split(":")
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    if USERS.get(username) == password:
        return username
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)


@app.get("/endpoint1")
def endpoint1(username: str = Depends(basic_auth)):
    return {"message": f"Welcome to endpoint 1, {username}"}

@app.get("/endpoint2")
def endpoint2(username: str = Depends(basic_auth)):
    return {"message": f"Welcome to endpoint 2, {username}"}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)