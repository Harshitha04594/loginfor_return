from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

# Enable CORS to allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dummy database of delivery agents
agents_db = {
    "agent1": "password123",
    "agent2": "securepass456"
}

# Login request model
class LoginRequest(BaseModel):
    name: str
    password: str

@app.post("/login")
async def login(data: LoginRequest):
    if data.name in agents_db and agents_db[data.name] == data.password:
        return {
            "status": "success",
            "message": "Login successful!",
            "redirect": "https://aipoweredfrauddetection.streamlit.app/"
        }
    else:
        raise HTTPException(status_code=401, detail="Invalid credentials!")