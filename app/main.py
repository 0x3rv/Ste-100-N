from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import auth, service
from app.middleware.jwt_middleware import JWTMiddleware

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(JWTMiddleware, excluded_routes=["/auth/signup", "/auth/login", "/auth/validate-token"])

app.include_router(auth.router)
app.include_router(service.router)

@app.get("/")
def root():
    return {"message": "FastAPI + JWT + Gemini + MongoDB"}
