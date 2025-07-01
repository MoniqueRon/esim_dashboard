from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from esim_routes import router as esim_router
from dotenv import load_dotenv
from datetime import datetime, timedelta, timezone
import os
import httpx

load_dotenv()

app = FastAPI()

# JWT config for dashboard login
SECRET_KEY = os.getenv("SECRET_KEY", "supersecret")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

# Local dashboard login
@app.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    username = os.getenv("DASHBOARD_USERNAME")
    password = os.getenv("DASHBOARD_PASSWORD")

    if form_data.username != username or form_data.password != password:
        raise HTTPException(status_code=401, detail="Invalid dashboard credentials")

    # Login to Nexuce and store JWT for API use
    nexuce_payload = {
        "userName": os.getenv("NEXUCE_USERNAME"),
        "password": os.getenv("NEXUCE_PASSWORD")
    }
    headers = {"Content-Type": "application/json"}

    print(f"Attempting Nexuce login with username: {nexuce_payload['userName']}")
    
    async with httpx.AsyncClient() as client:
        response = await client.post("https://mobileapp.roamability.com/portal/auth", json=nexuce_payload, headers=headers)
        print(f"Nexuce auth response: {response.status_code}")
        print(f"Nexuce auth headers: {dict(response.headers)}")
        
        if response.status_code != 200:
            print(f"Nexuce auth failed: {response.text}")
            raise HTTPException(status_code=500, detail=f"Failed to authenticate with Nexuce API: {response.status_code}")
        
        data = response.json()
        print(f"Nexuce auth success: {data}")
        app.state.nexuce_token = data.get("jwt")
        print(f"Stored JWT token: {app.state.nexuce_token[:50] if app.state.nexuce_token else 'None'}...")

    # Return local dashboard token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    expire = datetime.now(timezone.utc) + access_token_expires
    token_data = {"sub": form_data.username, "exp": expire}
    dashboard_token = jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)
    return {"access_token": dashboard_token, "token_type": "bearer"}

# Secure backend routes with dashboard JWT
async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("sub")
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

# Use Nexuce token behind protected routes
async def get_nexuce_token(current_user: str = Depends(get_current_user)):
    if not app.state.nexuce_token:
        raise HTTPException(status_code=403, detail="Not authenticated with Nexuce")
    return app.state.nexuce_token

# Include the ESIM routes
app.include_router(esim_router, dependencies=[Depends(get_current_user)])

