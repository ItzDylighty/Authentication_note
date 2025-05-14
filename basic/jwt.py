from jose import JWTError, jwt
from datetime import datetime, timedelta
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import secrets
import uvicorn

SECRET_KEY = "secret"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

VALID_USERS = {
    "admin": "admin123",
    "johndoe": "secret",
    "alice": "qwerty",
}

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_access_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None
    
def get_current_user(token: str = Depends(oauth2_scheme)):
    payload = decode_access_token(token)
    if not payload or "sub" not in payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return payload["username"]

@app.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    username = form_data.username
    password = form_data.password

    if username not in VALID_USERS or not secrets.compare_digest(VALID_USERS[username], password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )

    custom_claims = {}
    if username == "admin":
        custom_claims["priveledged"] = True

    access_token = create_access_token(data={"sub": username, "username": username, **custom_claims})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/normal-data")
def read_normal_data(current_user: str = Depends(get_current_user)):
    return {"message": f"Welcome, {current_user}. This is for all logged-in users."}

@app.get("/secure-data")
def read_secure_data(current_user: str = Depends(get_current_user)):
    return {"message": f"Hello, {current_user}. This is a secure endpoint."}


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)