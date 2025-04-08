# from starlette.middleware.base import BaseHTTPMiddleware
# from starlette.requests import Request
# from fastapi import HTTPException
# from app.utils.jwt_handler import decode_jwt

# import logging

# class JWTMiddleware(BaseHTTPMiddleware):
#     def __init__(self, app, excluded_routes=None):
#         super().__init__(app)
#         self.excluded_routes = excluded_routes or []

#     async def dispatch(self, request: Request, call_next):
#         # Exclude specific routes from authentication
#         if request.url.path in self.excluded_routes:
#             return await call_next(request)

#         token = request.headers.get("Authorization")
#         logging.info(f"Authorization header: {token}")
#         if token is None or not token.startswith("Bearer "):
#             raise HTTPException(status_code=401, detail="Authorization token missing or invalid")
        
#         try:
#             payload = decode_jwt(token.split(" ")[1])
#             request.state.user = payload
#         except Exception as e:
#             logging.error(f"Token decoding failed: {e}")
#             raise HTTPException(status_code=401, detail="Invalid token")
        
#         response = await call_next(request)
#         return response





from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response # Import Response for type hinting
from starlette.types import ASGIApp, Receive, Scope, Send # More specific ASGI types
from fastapi import HTTPException
from app.utils.jwt_handler import decode_jwt

import logging

class JWTMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp, excluded_routes: list[str] | None = None):
        super().__init__(app)
        # Use a set for efficient lookup
        self.excluded_routes = set(excluded_routes) if excluded_routes else set()

    async def dispatch(self, request: Request, call_next) -> Response:
        # --- CORRECTED PART ---
        # 1. Allow OPTIONS requests to pass through without authentication checks.
        # This must happen BEFORE checking for the Authorization header.
        if request.method == "OPTIONS":
            logging.debug(f"Allowing OPTIONS request for {request.url.path} to pass through.")
            return await call_next(request)
        # --- END CORRECTION ---

        # 2. Exclude specific routes from authentication
        # Use request.url.path which is a string, not request.url which is an object
        if request.url.path in self.excluded_routes:
            logging.debug(f"Request path {request.url.path} is excluded from JWT check.")
            return await call_next(request)

        # 3. Proceed with token extraction and validation for non-excluded routes
        token = request.headers.get("Authorization")
        # Use logging.debug for potentially sensitive info like tokens in logs
        # logging.info(f"Authorization header found for {request.url.path}") # Less verbose

        if token is None or not token.startswith("Bearer "):
            logging.warning(f"Missing or invalid Bearer token for {request.url.path}.")
            # Raising HTTPException here is generally okay, but sometimes returning a
            # JSONResponse directly gives more control, especially over headers.
            raise HTTPException(status_code=401, detail="Authorization token missing or invalid format")

        try:
            token_value = token.split(" ")[1]
            payload = decode_jwt(token_value)
            # Attach payload to request state for use in route handlers
            request.state.user = payload
            logging.debug(f"Token validated successfully for {request.url.path}. User: {payload.get('sub', 'N/A')}")
        except HTTPException as http_exc:
             # Re-raise HTTPException if decode_jwt raises it (e.g., specific validation error)
             logging.warning(f"Token validation HTTPException for {request.url.path}: {http_exc.detail}")
             raise http_exc
        except Exception as e:
            # Catch generic exceptions during decoding (ExpiredSignatureError, InvalidTokenError, etc.)
            logging.error(f"Token decoding failed for {request.url.path}: {e}", exc_info=True) # Log traceback
            raise HTTPException(status_code=401, detail=f"Invalid token: {e}") # Include error detail if safe

        # If token is valid, call the next middleware or the route handler
        response = await call_next(request)
        return response