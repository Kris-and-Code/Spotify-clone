from flask import Flask, request, jsonify, g
from flask_cors import CORS
from datetime import datetime, timedelta
import uuid
from models import User, Song, Playlist
from database import Database
from config import Config
from functools import wraps
import jwt
import bcrypt
from werkzeug.exceptions import HTTPException
from typing import Dict, Any

app = Flask(__name__)
CORS(app)

def create_access_token(user_id: str) -> str:
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(minutes=Config.ACCESS_TOKEN_EXPIRE_MINUTES)
    }
    return jwt.encode(payload, Config.JWT_SECRET_KEY, algorithm=Config.JWT_ALGORITHM)

def require_auth():
    def decorator(f):
        @wraps(f)
        async def wrapped(*args, **kwargs):
            token = request.headers.get('Authorization')
            if not token or not token.startswith('Bearer '):
                return jsonify({"error": "Missing or invalid authorization token"}), 401
            
            try:
                token = token.split(' ')[1]
                payload = jwt.decode(
                    token, 
                    Config.JWT_SECRET_KEY, 
                    algorithms=[Config.JWT_ALGORITHM]
                )
                g.user_id = payload['user_id']
            except jwt.ExpiredSignatureError:
                return jsonify({"error": "Token has expired"}), 401
            except jwt.InvalidTokenError:
                return jsonify({"error": "Invalid token"}), 401
                
            return await f(*args, **kwargs)
        return wrapped
    return decorator

# Add request validation middleware
def validate_request_json(required_fields: Dict[str, Any]):
    def decorator(f):
        @wraps(f)
        async def wrapper(*args, **kwargs):
            if not request.is_json:
                return jsonify({"error": "Content-Type must be application/json"}), 400
            
            data = request.json
            missing_fields = [field for field in required_fields if field not in data]
            
            if missing_fields:
                return jsonify({
                    "error": f"Missing required fields: {', '.join(missing_fields)}"
                }), 400
                
            return await f(*args, **kwargs)
        return wrapper
    return decorator

# User routes
@app.route('/api/users', methods=['POST'])
@validate_request_json(['username', 'email', 'password'])
async def create_user():
    data = request.json
    
    # Add password hashing
    hashed_password = bcrypt.hashpw(
        data['password'].encode('utf-8'), 
        bcrypt.gensalt()
    )
    
    user = User(
        id=str(uuid.uuid4()),
        username=data['username'],
        email=data['email'],
        password=hashed_password.decode('utf-8'),
        created_at=datetime.now()
    )
    
    user_id = await Database.create_user(user)
    token = create_access_token(user_id)
    
    return jsonify({
        "message": "User created successfully",
        "user_id": user_id,
        "access_token": token
    }), 201

@app.route('/api/users/<user_id>', methods=['GET'])
async def get_user(user_id):
    user = await Database.get_user(user_id)
    if user:
        return jsonify(user.dict()), 200
    return jsonify({"message": "User not found"}), 404

# Song routes
@app.route('/api/songs', methods=['POST'])
@require_auth()
@validate_request_json(['title', 'artist', 'album', 'duration', 'genre', 'release_date', 'audio_url'])
async def create_song():
    data = request.json
    try:
        # Validate duration is positive
        if not isinstance(data['duration'], int) or data['duration'] <= 0:
            return jsonify({"error": "Duration must be a positive integer"}), 400
            
        # Validate release_date format
        release_date = datetime.fromisoformat(data['release_date'])
        
        song = Song(
            id=str(uuid.uuid4()),
            title=data['title'],
            artist=data['artist'],
            album=data['album'],
            duration=data['duration'],
            genre=data['genre'],
            release_date=release_date,
            audio_url=data['audio_url'],
            cover_image=data.get('cover_image', ''),  # Make cover_image optional
            created_at=datetime.now()
        )
        song_id = await Database.create_song(song)
        return jsonify({"message": "Song created successfully", "song_id": song_id}), 201
    except ValueError as e:
        return jsonify({"error": f"Invalid date format: {str(e)}"}), 400

@app.route('/api/songs/<song_id>', methods=['GET'])
async def get_song(song_id):
    song = await Database.get_song(song_id)
    if song:
        return jsonify(song.dict()), 200
    return jsonify({"message": "Song not found"}), 404

@app.route('/api/songs/search', methods=['GET'])
async def search_songs():
    query = request.args.get('q', '')
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 20))
    
    if len(query) < 2:
        return jsonify({
            "error": "Search query must be at least 2 characters long"
        }), 400
        
    try:
        songs = await Database.search_songs(query, page, per_page)
        return jsonify({
            "songs": [song.dict() for song in songs],
            "page": page,
            "per_page": per_page
        }), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

# Playlist routes
@app.route('/api/playlists', methods=['POST'])
@require_auth()
@validate_request_json(['name'])
async def create_playlist():
    data = request.json
    playlist = Playlist(
        id=str(uuid.uuid4()),
        name=data['name'],
        description=data.get('description'),
        owner_id=g.user_id,
        songs=data.get('songs', []),
        followers=[],
        cover_image=data.get('cover_image'),
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    
    # Validate that all song IDs exist
    if playlist.songs:
        for song_id in playlist.songs:
            if not await Database.get_song(song_id):
                return jsonify({
                    "error": f"Song with ID {song_id} does not exist"
                }), 400
    
    playlist_id = await Database.create_playlist(playlist)
    return jsonify({
        "message": "Playlist created successfully",
        "playlist_id": playlist_id
    }), 201

@app.route('/api/playlists/<playlist_id>', methods=['GET'])
async def get_playlist(playlist_id):
    playlist = await Database.get_playlist(playlist_id)
    if playlist:
        return jsonify(playlist.dict()), 200
    return jsonify({"message": "Playlist not found"}), 404

@app.route('/api/playlists/<playlist_id>', methods=['PUT'])
@require_auth()
async def update_playlist(playlist_id):
    data = request.json
    
    # Check if playlist exists and user owns it
    playlist = await Database.get_playlist(playlist_id)
    if not playlist:
        return jsonify({"error": "Playlist not found"}), 404
    
    if playlist.owner_id != g.user_id:
        return jsonify({"error": "Not authorized to modify this playlist"}), 403
    
    # Validate song IDs if they're being updated
    if 'songs' in data:
        for song_id in data['songs']:
            if not await Database.get_song(song_id):
                return jsonify({
                    "error": f"Song with ID {song_id} does not exist"
                }), 400
    
    success = await Database.update_playlist(playlist_id, data)
    return jsonify({"message": "Playlist updated successfully"}), 200

@app.route('/api/users/<user_id>/playlists', methods=['GET'])
async def get_user_playlists(user_id):
    playlists = await Database.get_user_playlists(user_id)
    return jsonify([playlist.dict() for playlist in playlists]), 200

# Add error handling middleware
@app.errorhandler(Exception)
def handle_error(error):
    code = 500
    message = str(error)
    
    if isinstance(error, HTTPException):
        code = error.code
    elif isinstance(error, ValueError):
        code = 400
    elif isinstance(error, jwt.InvalidTokenError):
        code = 401
        message = "Invalid authentication token"
    
    return jsonify({
        'error': message,
        'status_code': code
    }), code

if __name__ == '__main__':
    app.run(debug=True) 