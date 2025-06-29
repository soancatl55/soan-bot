from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
import os
from urllib.parse import urlencode

app = FastAPI()

# Datos de tu app de Twitch
CLIENT_ID = "1voc07kf8akhgki847ntwi2yx6itep"
REDIRECT_URI = "https://web-production-b3389.up.railway.app/auth/twitch/callback"

@app.get("/")
def read_root():
    return {"message": "Hola Mundo desde Railway"}

@app.get("/login")
def login():
    # Parámetros OAuth para Twitch
    params = {
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "response_type": "code",
        "scope": "user:read:email"
    }
    # Construir la URL de autenticación de Twitch
    twitch_auth_url = "https://id.twitch.tv/oauth2/authorize?" + urlencode(params)
    return RedirectResponse(twitch_auth_url)
