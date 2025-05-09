from contextlib import asynccontextmanager

from fastapi import FastAPI
from starlette.staticfiles import StaticFiles

from src.core import redis_client, database_helper
from src.auth.routes import router as auth_router
from src.websocket.routes import router as websocket_router
from src.users.routes import router as user_router
from src.complaints.complaint_routes import router as complaint_router
from src.comments.routes import router as comment_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    await redis_client.connect()

    yield

    await redis_client.close()
    await database_helper.dispose()

app = FastAPI(lifespan=lifespan)

app.mount('/static', StaticFiles(directory="static"), name='static')

app.include_router(auth_router)
app.include_router(user_router)
app.include_router(complaint_router)
app.include_router(comment_router)
app.include_router(websocket_router)


