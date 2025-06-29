from fastapi import FastAPI, Request, Query
from fastapi.responses import RedirectResponse, JSONResponse
import httpx
from urllib.parse import urlencode
from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI()

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI")

@app.get("/")
def read_root():
    return {"message": "Hola Mundo desde Railway"}

@app.get("/login")
def login(channel: str = Query(..., description="Nombre del canal Twitch a monitorear")):
    params = {
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "response_type": "code",
        "scope": "user:read:email user:read:follows",
        "state": channel
    }
    twitch_auth_url = "https://id.twitch.tv/oauth2/authorize?" + urlencode(params)
    return RedirectResponse(twitch_auth_url)

@app.get("/auth/twitch/callback")
async def auth_callback(request: Request):
    code = request.query_params.get("code")
    state = request.query_params.get("state")  # Aquí recibimos el canal

    if not code:
        return JSONResponse({"error": "No se recibió el código de autorización"}, status_code=400)

    if not state:
        return JSONResponse({"error": "No se recibió el parámetro state (canal)"}, status_code=400)

    channel = state

    async with httpx.AsyncClient() as client:
        token_response = await client.post("https://id.twitch.tv/oauth2/token", data={
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": REDIRECT_URI
        })
        token_data = token_response.json()

        if "access_token" not in token_data:
            return JSONResponse({"error": "No se pudo obtener el access token", "details": token_data}, status_code=400)

        access_token = token_data["access_token"]

        headers = {
            "Client-ID": CLIENT_ID,
            "Authorization": f"Bearer {access_token}"
        }

        # Obtener info del usuario autenticado
        user_response = await client.get("https://api.twitch.tv/helix/users", headers=headers)
        user_data = user_response.json()

        if "data" not in user_data or len(user_data["data"]) == 0:
            return JSONResponse({"error": "No se pudo obtener información del usuario"}, status_code=400)

        user_info = user_data["data"][0]
        user_id = user_info["id"]

        # Obtener info del canal dinámico recibido en state
        channel_response = await client.get(f"https://api.twitch.tv/helix/users?login={channel}", headers=headers)
        channel_data = channel_response.json()

        if "data" not in channel_data or len(channel_data["data"]) == 0:
            return JSONResponse({"error": "No se encontró el canal para monitorear"}, status_code=400)

        channel_info = channel_data["data"][0]
        channel_id = channel_info["id"]

        # Consultar si el usuario sigue al canal
        follows_response = await client.get(f"https://api.twitch.tv/helix/users/follows?from_id={user_id}&to_id={channel_id}", headers=headers)
        follows_data = follows_response.json()

        is_following = (follows_data.get("total", 0) > 0)

    return {
        "user": user_info,
        "channel": channel_info,
        "is_following": is_following
    }
