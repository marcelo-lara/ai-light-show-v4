from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes import health, songs, render, playback, canvas
from ws.router import router as ws_router

app = FastAPI(title="ai-light-show", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3400"],
    allow_methods=["*"],
    allow_headers=["*"],
)

for r in (health.router, songs.router, render.router, playback.router, canvas.router):
    app.include_router(r)

app.include_router(ws_router)
