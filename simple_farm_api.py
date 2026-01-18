import os
from dotenv import load_dotenv
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException


load_dotenv()

app = FastAPI(title=os.getenv("APP_NAME", "Default Farm API"))

@app.get("/config")
def get_config():
    return {
        "app_name": os.getenv("APP_NAME"),
        "debug": os.getenv("DEBUG", "False")
    }

app = FastAPI()

# Simple data storage (in real app, this would be a database)
pigs = [
    {"tag_number": "001", "gender": "Sow", "breed": "Landrace"},
    {"tag_number": "002", "gender": "Boar", "breed": "Duroc"}
]

class Pig(BaseModel):
    tag_number: str
    gender: str
    breed: str

@app.get("/")
def read_root():
    return {"message": "Simple Farm API"}

@app.get("/pigs")
def get_pigs():
    return {"pigs": pigs}

@app.get("/pigs/count")
def count_pigs():
    return {"total": len(pigs)}

@app.post("/pigs")
def add_pig(pig: Pig):
    pigs.append(pig.dict())
    return {"message": f"Added pig {pig.tag_number}"}

@app.get("/pigs/{tag_number}")
def get_pig(tag_number: str):
    for pig in pigs:
        if pig["tag_number"] == tag_number:
            return pig
    
    # If pig not found, return 404 error
    raise HTTPException(status_code=404, detail="Pig not found")