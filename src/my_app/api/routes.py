"""API routes."""

from fastapi import APIRouter
from pydantic import BaseModel
from my_app.core.services import greet

router = APIRouter()


class GreetRequest(BaseModel):
    name: str


class GreetResponse(BaseModel):
    message: str


@router.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Welcome to My App"}


@router.post("/greet", response_model=GreetResponse)
async def greet_endpoint(request: GreetRequest):
    """Greet a user."""
    message = greet(request.name)
    return GreetResponse(message=message)