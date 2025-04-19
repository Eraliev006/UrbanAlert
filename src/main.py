import uvicorn
from fastapi import FastAPI

from src.core import settings
from auth.routes import router as auth_router

app = FastAPI()

app.include_router(auth_router)

if __name__ == "__main__":
    uvicorn.run(
        'main:app',
        port=settings.server_port,
        host=settings.server_host,
    )



