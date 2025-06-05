from fastapi import FastAPI, Request, Query
from fastapi.responses import HTMLResponse, RedirectResponse
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
from spotipy.exceptions import SpotifyException

REDIRECT_URI = "http://127.0.0.1:8000/callback"
SCOPE = "user-top-read"

if os.path.exists(".cache"):
    os.remove(".cache")

app = FastAPI()

sp_oauth = SpotifyOAuth(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    redirect_uri=REDIRECT_URI,
    scope=SCOPE
)
token_info = {}

@app.get("/", response_class=HTMLResponse)
def login():
    auth_url = sp_oauth.get_authorize_url()
    html = f"<h1>Login with Spotify</h1><a href='{auth_url}'>Click here to log in</a>"
    return HTMLResponse(content=html)

@app.get("/callback")
def callback(request: Request):
    code = request.query_params.get("code")
    global token_info
    token_info = sp_oauth.get_access_token(code)
    return RedirectResponse(url="/mood-tracks?mood=50")

@app.get("/mood-tracks")
def mood_tracks(mood: int = Query(50, ge=0, le=100)):
    global token_info
    if not token_info:
        return HTMLResponse("Not logged in! Go to / to login.")
    
    access_token = token_info["access_token"]
    sp = spotipy.Spotify(auth=access_token)

    top_artists = sp.current_user_top_artists(limit=5)
    seed_artists = [artist["id"] for artist in top_artists["items"]]
    mood_val = mood / 100.0

   try:␊
        recs = sp.recommendations(
            seed_artists=seed_artists[:2],
            target_energy=mood_val,
            target_valence=mood_val,
            limit=10
        )
        if not recs["tracks"]:
            raise Exception("Empty recommendations from artist seeds")
    except SpotifyException:
        recs = sp.recommendations(
            seed_genres=["pop", "rock"],
            target_energy=mood_val,
            target_valence=mood_val,
            limit=10
        )

    html = f"<h1>Recommendations for mood {mood}</h1><ul>"
    for track in recs["tracks"]:
        html += f"<li>{track['name']} by {track['artists'][0]['name']}</li>"
    html += "</ul>"
    
    return HTMLResponse(content=html)



@app.get("/test-recs")
def test_recommendations():
    access_token = token_info.get("access_token")
    if not access_token:
        return HTMLResponse("Not logged in!")
    
    sp = spotipy.Spotify(auth=access_token)
    try:
        recs = sp.recommendations(
            seed_genres=["pop"],
            limit=5
        )
    except Exception as e:
        return HTMLResponse(f"Error: {str(e)}")

    html = "<h1>Test Recommendations</h1><ul>"
    for track in recs["tracks"]:
        html += f"<li>{track['name']} by {track['artists'][0]['name']}</li>"
    html += "</ul>"
    return HTMLResponse(html)
