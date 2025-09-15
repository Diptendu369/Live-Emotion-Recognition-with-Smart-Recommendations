import os
import time
import base64
from typing import List, Dict
import requests
from urllib.parse import urlencode

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY", "")
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID", "")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET", "")

_spotify_token_cache = {"access_token": None, "expires_at": 0}


def _emotion_keywords(emotion: str, age: int | None, gender: str | None) -> str:
    e = (emotion or "").lower()
    base = {
        "happy": "uplifting happy",
        "sad": "soothing sad",
        "angry": "calming chill",
        "fear": "comforting acoustic",
        "disgust": "fresh upbeat",
        "surprise": "energetic surprise",
        "neutral": "relaxing focus"
    }.get(e, "relaxing focus")
    if gender:
        base += f" {gender}"
    if isinstance(age, int):
        if age < 18:
            base += " teen"
        elif age < 30:
            base += " young adult"
        elif age < 50:
            base += " adult"
        else:
            base += " classic"
    return base


def _youtube_search(query: str, max_results: int = 5) -> List[Dict]:
    if not YOUTUBE_API_KEY:
        return []
    params = {
        "part": "snippet",
        "q": query,
        "type": "video",
        "maxResults": max_results,
        "key": YOUTUBE_API_KEY,
        "safeSearch": "moderate",
        "videoEmbeddable": "true",
    }
    r = requests.get("https://www.googleapis.com/youtube/v3/search", params=params, timeout=10)
    items = []
    if r.ok:
        data = r.json()
        for it in data.get("items", []):
            vid = it.get("id", {}).get("videoId")
            title = it.get("snippet", {}).get("title")
            if vid and title:
                items.append({
                    "title": title,
                    "url": f"https://www.youtube.com/watch?v={vid}",
                    "source": "youtube"
                })
    return items


def _spotify_token() -> str | None:
    now = int(time.time())
    if _spotify_token_cache["access_token"] and _spotify_token_cache["expires_at"] - 30 > now:
        return _spotify_token_cache["access_token"]
    if not (SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET):
        return None
    auth = base64.b64encode(f"{SPOTIFY_CLIENT_ID}:{SPOTIFY_CLIENT_SECRET}".encode()).decode()
    headers = {"Authorization": f"Basic {auth}", "Content-Type": "application/x-www-form-urlencoded"}
    data = {"grant_type": "client_credentials"}
    r = requests.post("https://accounts.spotify.com/api/token", headers=headers, data=data, timeout=10)
    if r.ok:
        tok = r.json()
        _spotify_token_cache["access_token"] = tok.get("access_token")
        _spotify_token_cache["expires_at"] = now + int(tok.get("expires_in", 3600))
        return _spotify_token_cache["access_token"]
    return None


def _spotify_search(query: str, max_results: int = 5) -> List[Dict]:
    token = _spotify_token()
    if not token:
        return []
    headers = {"Authorization": f"Bearer {token}"}
    params = {"q": query, "type": "track", "limit": max_results}
    r = requests.get("https://api.spotify.com/v1/search", headers=headers, params=params, timeout=10)
    items = []
    if r.ok:
        data = r.json()
        for tr in data.get("tracks", {}).get("items", []):
            name = tr.get("name")
            url = tr.get("external_urls", {}).get("spotify")
            if name and url:
                items.append({
                    "title": name,
                    "url": url,
                    "source": "spotify"
                })
    return items


def get_recommendations(emotion: str | None, age: int | None = None, gender: str | None = None) -> List[Dict]:
    query = _emotion_keywords(emotion, age, gender)
    videos = _youtube_search(query)
    tracks = _spotify_search(query)
    results = videos + tracks
    if not results:
        # basic fallback links
        return [
            {"title": "Lofi beats", "url": "https://www.youtube.com/watch?v=5qap5aO4i9A", "source": "youtube"}
        ]
    return results[:10]
