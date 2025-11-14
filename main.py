import os
import dotenv

from fastapi import FastAPI
import logging
from fastapi.middleware.cors import CORSMiddleware

import config
from app.router import router
from app.user_router import user_router
from utils.db import init_db

dotenv.load_dotenv()

logger = logging.getLogger(__name__)


app = FastAPI()


@app.on_event("startup")
async def on_startup():
    logger.info("App startup: initializing DB.")
    await init_db()


origins = [
    "http://localhost:3000",
    "http://localhost:8000",
]


env_orgs = os.getenv("FRONTEND_URL").split(",")
for origin in env_orgs:
    if origin not in origins:
        origins.append(origin)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)
app.include_router(user_router, prefix="/user")
