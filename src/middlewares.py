import time
from logging import getLogger
from typing import Callable, Awaitable

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import Response

from src.core import settings

type CallNext = Callable[[Request], Awaitable[Response]]

logger = getLogger('fixkg.middlewares')

def register_middleware(app: FastAPI):

    @app.middleware('http')
    async def log_new_request_and_response(
            request: Request,
            call_next: CallNext
    ) -> Response:
        logger.info('REQUESTS - %s - %s - %s - %s', request.method, request.url, request.client.host, request.headers)

        response: Response = await call_next(request)
        logger.info('RESPONSE - %d - %s', response.status_code, response.headers)
        return response

    @app.middleware('http')
    async def add_process_time_to_requests(
            request: Request,
            call_next: CallNext
    ) -> Response:
        start = time.perf_counter()
        response = await call_next(request)
        process_time = time.perf_counter() - start

        response.headers['X-process-time'] = f'Process time: {process_time:.5f}'
        return response

    app.add_middleware(
        CORSMiddleware,
        allow_origins = settings.ALLOW_ORIGINS,
        allow_methods = settings.ALLOW_METHODS,
        allow_headers = settings.ALLOW_HEADERS
    )

