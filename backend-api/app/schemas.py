"""Pydantic models for parsing data from and returning data to API requests."""
from typing import List, Optional
from pydantic import BaseModel


class Device(BaseModel):
    id: int
    device_name: str
    user_id: int

    class Config:
        orm_mode = True


class User(BaseModel):
    id: int
    username: str
    devices: List[Device] = []

    class Config:
        orm_mode = True