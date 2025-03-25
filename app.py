from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
import uuid
from models import User, Song, Playlist
from database import Database
from config import Config

app = Flask(__name__)
CORS(app)

# User routes
@app.route('/api/users', methods=['POST'])
async def create_user():
    data = request.json
    user = User(
        id=str(uuid.uuid4()),
        username=data['username'],
        email=data['email'],
        created_at=datetime.now()
    )
    user_id = await Database.create_user(user)
    return jsonify({"message": "User created successfully", "user_id": user_id}), 201

@app.route('/api/users/<user_id>', methods=['GET'])
async def get_user(user_id):
    user = await Database.get_user(user_id)
    if user:
        return jsonify(user.dict()), 200
    return jsonify({"message": "User not found"}), 404

# Song routes
@app.route('/api/songs', methods=['POST'])
async def create_song():
    data = request.json
    song = Song(
        id=str(uuid.uuid4()),
        title=data['title'],
        artist=data['artist'],
        album=data['album'],
        duration=data['duration'],
        genre=data['genre'],
        release_date=datetime.fromisoformat(data['release_date']),
        audio_url=data['audio_url'],
        cover_image=data['cover_image'],
        created_at=datetime.now()
    )
    song_id = await Database.create_song(song)
    return jsonify({"message": "Song created successfully", "song_id": song_id}), 201

@app.route('/api/songs/<song_id>', methods=['GET'])
async def get_song(song_id):
    song = await Database.get_song(song_id)
    if song:
        return jsonify(song.dict()), 200
    return jsonify({"message": "Song not found"}), 404

@app.route('/api/songs/search', methods=['GET'])
async def search_songs():
    query = request.args.get('q', '')
    songs = await Database.search_songs(query)
    return jsonify([song.dict() for song in songs]), 200

# Playlist routes
@app.route('/api/playlists', methods=['POST'])
async def create_playlist():
    data = request.json
    playlist = Playlist(
        id=str(uuid.uuid4()),
        name=data['name'],
        description=data.get('description'),
        owner_id=data['owner_id'],
        songs=data.get('songs', []),
        followers=data.get('followers', []),
        cover_image=data.get('cover_image'),
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    playlist_id = await Database.create_playlist(playlist)
    return jsonify({"message": "Playlist created successfully", "playlist_id": playlist_id}), 201

@app.route('/api/playlists/<playlist_id>', methods=['GET'])
async def get_playlist(playlist_id):
    playlist = await Database.get_playlist(playlist_id)
    if playlist:
        return jsonify(playlist.dict()), 200
    return jsonify({"message": "Playlist not found"}), 404

@app.route('/api/playlists/<playlist_id>', methods=['PUT'])
async def update_playlist(playlist_id):
    data = request.json
    success = await Database.update_playlist(playlist_id, data)
    if success:
        return jsonify({"message": "Playlist updated successfully"}), 200
    return jsonify({"message": "Playlist not found"}), 404

@app.route('/api/users/<user_id>/playlists', methods=['GET'])
async def get_user_playlists(user_id):
    playlists = await Database.get_user_playlists(user_id)
    return jsonify([playlist.dict() for playlist in playlists]), 200

if __name__ == '__main__':
    app.run(debug=True) 