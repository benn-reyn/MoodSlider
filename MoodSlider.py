from fastapi import FastAPI, Request, Query
from fastapi.responses import HTMLResponse, RedirectResponse
import spotipy
from spotipy.oauth2 import SpotifyOAuth

app = FastAPI()

print("🚀 MoodSliderTest is loaded!")

# Your Spotify App credentials
CLIENT_ID = "3b7394e4910743c0852fa0811ba9679f"
CLIENT_SECRET = "6b8ff28643bf4ca59b6a3b33bcf40160"
REDIRECT_URI = "http://127.0.0.1:8000/callback"
SCOPE = "user-top-read"

sp_oauth = SpotifyOAuth(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    redirect_uri=REDIRECT_URI,
    scope=SCOPE
)

# Store tokens globally for simplicity in testing
token_info = {}

@app.get("/")
def login():
    auth_url = sp_oauth.get_authorize_url()
    return HTMLResponse(f"<a href='{auth_url}'>Login with Spotify</a>")

@app.get("/callback")
def callback(request: Request):
    code = request.query_params.get("code")
    global token_info
    token_info = sp_oauth.get_access_token(code)
    
    # Auto-redirect to mood slider endpoint instead of showing top tracks
    return RedirectResponse(url="/mood-tracks?mood=50")

@app.get("/mood-tracks")
def mood_tracks(mood: int = Query(50, ge=0, le=100)):
    global token_info
    if not token_info:
        return HTMLResponse("Please login first at /")
    
    access_token = token_info["access_token"]
    sp = spotipy.Spotify(auth=access_token)
    
    # Get user's top artists
    top_artists = sp.current_user_top_artists(limit=5)
    seed_artists = [artist["id"] for artist in top_artists["items"]]
    
    # Get genres from top artists (or fallback)
    genres = []
    for artist in top_artists["items"]:
        genres.extend(artist["genres"])
    if not genres:
        genres = ["pop", "rock"]

    # Map mood slider input to 0.0 - 1.0
    mood_val = mood / 100.0
    
    # Get recommendations based on mood and top artists
    recs = sp.recommendations(
        seed_artists=seed_artists[:2],
        seed_genres=genres[:2],
        target_energy=mood_val,
        target_valence=mood_val,
        limit=10
    )
    
    # Display recommended tracks
    html = f"<h1>Recommendations for mood {mood}</h1><ul>"
    for track in recs["tracks"]:
        html += f"<li>{track['name']} by {track['artists'][0]['name']}</li>"
    html += "</ul>"
    
    return HTMLResponse(html)

    