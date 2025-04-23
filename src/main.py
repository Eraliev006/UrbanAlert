import uvicorn
from fastapi import FastAPI

from src.core import settings
from auth.routes import router as auth_router
from users.routes import router as user_router

app = FastAPI()

app.include_router(auth_router)
app.include_router(user_router)

if __name__ == "__main__":
    uvicorn.run(
        'main:app',
        port=settings.server_port,
        host=settings.server_host,
    )



