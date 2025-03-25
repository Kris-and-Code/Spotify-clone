import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime
from typing import List, Optional, Dict, Any
from models import User, Song, Playlist

# Initialize Firebase Admin
cred = credentials.Certificate('firebase-credentials.json')
firebase_admin.initialize_app(cred)
db = firestore.client()

class Database:
    @staticmethod
    async def create_user(user: User) -> str:
        user_dict = user.dict()
        user_dict['created_at'] = datetime.now()
        doc_ref = db.collection('users').document()
        doc_ref.set(user_dict)
        return doc_ref.id

    @staticmethod
    async def get_user(user_id: str) -> Optional[User]:
        doc_ref = db.collection('users').document(user_id)
        doc = doc_ref.get()
        if doc.exists:
            return User(**doc.to_dict())
        return None

    @staticmethod
    async def create_song(song: Song) -> str:
        song_dict = song.dict()
        song_dict['created_at'] = datetime.now()
        doc_ref = db.collection('songs').document()
        doc_ref.set(song_dict)
        return doc_ref.id

    @staticmethod
    async def get_song(song_id: str) -> Optional[Song]:
        doc_ref = db.collection('songs').document(song_id)
        doc = doc_ref.get()
        if doc.exists:
            return Song(**doc.to_dict())
        return None

    @staticmethod
    async def create_playlist(playlist: Playlist) -> str:
        playlist_dict = playlist.dict()
        playlist_dict['created_at'] = datetime.now()
        playlist_dict['updated_at'] = datetime.now()
        doc_ref = db.collection('playlists').document()
        doc_ref.set(playlist_dict)
        return doc_ref.id

    @staticmethod
    async def get_playlist(playlist_id: str) -> Optional[Playlist]:
        doc_ref = db.collection('playlists').document(playlist_id)
        doc = doc_ref.get()
        if doc.exists:
            return Playlist(**doc.to_dict())
        return None

    @staticmethod
    async def update_playlist(playlist_id: str, data: Dict[str, Any]) -> bool:
        doc_ref = db.collection('playlists').document(playlist_id)
        if doc_ref.get().exists:
            data['updated_at'] = datetime.now()
            doc_ref.update(data)
            return True
        return False

    @staticmethod
    async def search_songs(query: str) -> List[Song]:
        songs_ref = db.collection('songs')
        query = query.lower()
        results = []
        for doc in songs_ref.stream():
            song_data = doc.to_dict()
            if (query in song_data['title'].lower() or 
                query in song_data['artist'].lower() or 
                query in song_data['album'].lower()):
                results.append(Song(**song_data))
        return results

    @staticmethod
    async def get_user_playlists(user_id: str) -> List[Playlist]:
        playlists_ref = db.collection('playlists')
        results = []
        for doc in playlists_ref.where('owner_id', '==', user_id).stream():
            results.append(Playlist(**doc.to_dict()))
        return results 