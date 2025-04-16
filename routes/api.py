from fastapi import APIRouter, Depends, HTTPException
from nicegui import app

router = APIRouter()

@router.get("/test")
async def test_endpoint():
    return {"message": "API funciona!"}
