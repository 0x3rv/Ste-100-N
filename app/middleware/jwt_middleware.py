from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from fastapi import HTTPException
from app.utils.jwt_handler import decode_jwt

import logging

class JWTMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, excluded_routes=None):
        super().__init__(app)
        self.excluded_routes = excluded_routes or []

    async def dispatch(self, request: Request, call_next):
        # Exclude specific routes from authentication
        if request.url.path in self.excluded_routes:
            return await call_next(request)

        token = request.headers.get("Authorization")
        logging.info(f"Authorization header: {token}")
        if token is None or not token.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Authorization token missing or invalid")
        
        try:
            payload = decode_jwt(token.split(" ")[1])
            request.state.user = payload
        except Exception as e:
            logging.error(f"Token decoding failed: {e}")
            raise HTTPException(status_code=401, detail="Invalid token")
        
        response = await call_next(request)
        return response