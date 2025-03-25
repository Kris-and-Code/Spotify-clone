# Spotify Clone Backend

A Python-based backend for a Spotify clone using Firebase Firestore as the database.

## Features

- User management (create, get user details)
- Song management (create, get, search songs)
- Playlist management (create, get, update playlists)
- User playlists
- Song search functionality

## Prerequisites

- Python 3.8+
- Firebase project with Firestore enabled
- Firebase Admin SDK credentials

## Setup

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Create a Firebase project and download the service account credentials
4. Rename your Firebase credentials file to `firebase-credentials.json` and place it in the root directory
5. Create a `.env` file with the following variables:
   ```
   JWT_SECRET_KEY=your-secret-key
   ```

## Running the Application

```bash
python app.py
```

The server will start on `http://localhost:5000`

## API Endpoints

### Users
- `POST /api/users` - Create a new user
- `GET /api/users/<user_id>` - Get user details

### Songs
- `POST /api/songs` - Create a new song
- `GET /api/songs/<song_id>` - Get song details
- `GET /api/songs/search?q=<query>` - Search songs

### Playlists
- `POST /api/playlists` - Create a new playlist
- `GET /api/playlists/<playlist_id>` - Get playlist details
- `PUT /api/playlists/<playlist_id>` - Update playlist
- `GET /api/users/<user_id>/playlists` - Get user's playlists

## Data Models

### User
- id: string
- username: string
- email: string
- created_at: datetime
- profile_image: string (optional)
- followers: string[]
- following: string[]

### Song
- id: string
- title: string
- artist: string
- album: string
- duration: integer
- genre: string
- release_date: datetime
- audio_url: string
- cover_image: string
- created_at: datetime

### Playlist
- id: string
- name: string
- description: string (optional)
- owner_id: string
- songs: string[]
- followers: string[]
- cover_image: string (optional)
- created_at: datetime
- updated_at: datetime 