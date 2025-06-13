from dotenv import load_dotenv
import os
import base64
import requests
import json
from spotipy import Spotify
from spotipy.oauth2 import SpotifyClientCredentials
from spotipy.exceptions import SpotifyException

load_dotenv()

client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")

auth_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
sp = Spotify(auth_manager=auth_manager)

# Mood mapping based on general genre mood associations
GENRE_TO_MOOD = {
    "pop": "vibrant",
    "dance": "vibrant",
    "edm": "vibrant",
    "house": "vibrant",
    "hip hop": "ambitious",
    "rap": "ambitious",
    "rock": "frustrated",
    "punk": "frustrated",
    "metal": "frustrated",
    "emo": "upset",
    "acoustic": "upset",
    "sad": "upset",
    "blues": "upset",
    "soul": "upset"
}

def get_token():
    auth = f"{client_id}:{client_secret}".encode()
    b64 = base64.b64encode(auth).decode()
    resp = requests.post(
        "https://accounts.spotify.com/api/token",
        headers={"Authorization": f"Basic {b64}"},
        data={"grant_type": "client_credentials"}
    )
    resp.raise_for_status()
    return resp.json()["access_token"]

token = get_token()

def search_for_artist(artist_name):
    result = sp.search(q=f"artist:{artist_name}", type="artist", limit=1)
    items = result["artists"]["items"]
    return items[0] if items else None

def get_songs_by_artist(artist_name: str, limit: int = 20, market: str = "US", use_top_tracks: bool = True):
    artist = search_for_artist(artist_name)
    if not artist:
        return []
    artist_id = artist["id"]

    if use_top_tracks:
        resp = sp.artist_top_tracks(artist_id, country=market)
        return resp["tracks"][:limit], artist["genres"]
    else:
        query = f"artist:{artist_name}"
        resp = sp.search(q=query, type="track", limit=limit, market=market)
        return resp["tracks"]["items"], artist["genres"]

def classify_genre_to_mood(genres):
    genre_str = ", ".join(genres).lower()
    for keyword, mood in GENRE_TO_MOOD.items():
        if keyword in genre_str:
            return mood
    return "vibrant" 

if __name__ == "__main__":
    artist_name = "Linkin Park"
    tracks, genres = get_songs_by_artist(artist_name, limit=5)
    mood = classify_genre_to_mood(genres)

    print(f"Top songs for {artist_name} classified under mood: {mood.upper()}")
    print("Genres:", genres)
    for track in tracks:
        print("-", track["name"])









    # Full search approach
    #search_tracks = get_songs_by_artist("AC/DC", limit=5, use_top_tracks=False)
    #for t in search_tracks:
        #print(t["name"], "-", t["artists"])


#--------------MOOD SLIDER-----------------

#metrics: acousticness, analysis_url, danceability, duration_ms, energy, id, instrumentalness, key, liveness, loudness, mode, speechiness,
#tempo, time_signature, track_href, type, uri, valence



     

#return access token-> access_token
#user access token in requests to Web API -> access_token
#return requested (unscoped data)->JSON obj

'''
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
'''
