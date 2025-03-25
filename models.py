from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class User(BaseModel):
    id: str
    username: str
    email: str
    created_at: datetime
    profile_image: Optional[str] = None
    followers: List[str] = []
    following: List[str] = []

class Song(BaseModel):
    id: str
    title: str
    artist: str
    album: str
    duration: int  # in seconds
    genre: str
    release_date: datetime
    audio_url: str
    cover_image: str
    created_at: datetime

class Playlist(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    owner_id: str
    songs: List[str] = []  # List of song IDs
    followers: List[str] = []
    cover_image: Optional[str] = None
    created_at: datetime
    updated_at: datetime 