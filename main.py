from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse, JSONResponse
import httpx
from urllib.parse import urlencode

app = FastAPI()

CLIENT_ID = "1voc07kf8akhgki847ntwi2yx6itep"
CLIENT_SECRET = "f0pfnob42ftah6q0cyf66syhq3w7me"
REDIRECT_URI = "https://web-production-b3389.up.railway.app/auth/twitch/callback"

@app.get("/")
def read_root():
    return {"message": "Hola Mundo desde Railway"}

@app.get("/login")
def login():
    params = {
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "response_type": "code",
        "scope": "user:read:email"
    }
    twitch_auth_url = "https://id.twitch.tv/oauth2/authorize?" + urlencode(params)
    return RedirectResponse(twitch_auth_url)

@app.get("/auth/twitch/callback")
async def auth_callback(request: Request):
    code = request.query_params.get("code")
    if not code:
        return JSONResponse({"error": "No se recibió el código de autorización"}, status_code=400)

    # Intercambiar el código por un token de acceso
    async with httpx.AsyncClient() as client:
        response = await client.post("https://id.twitch.tv/oauth2/token", data={
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": REDIRECT_URI
        })

    token_data = response.json()
    return token_data
