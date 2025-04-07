from fastapi import APIRouter, Depends, Header, HTTPException
from app.schemas.user import UserCreate, UserLogin, ForgotPassword, UserResponse, SignupResponse
from app.services.auth_service import register_user, login_user
from app.services.auth_service import verify_user
from app.services.auth_service import validate_token_service

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/signup", response_model=SignupResponse)
async def signup(user: UserCreate):
    return await register_user(user.email, user.password)

@router.post("/login", response_model=UserResponse)
async def login(user: UserLogin):
    return await login_user(user.email, user.password)

@router.post("/forgot-password")
async def forgot_password(data: ForgotPassword):
    # Just a placeholder
    return {"message": "Reset link sent to your email (not really)."}

@router.post("/verify-email")
async def verify_email(verification_code: str):
    return await verify_user(verification_code)


@router.post("/validate-token")
async def token_validation(authorization: str = Header(None)):
    """
    Validates a JWT token from Authorization header and returns user information if valid.
    """
    if not authorization or not authorization.startswith("Bearer "):
        return {"valid": False, "error": "Invalid authorization header"}
    
    try:
        # Extract the token from the "Bearer <token>" format
        token = authorization.split(" ")[1]
        validation_result = await validate_token_service(token)
        
        if not validation_result["valid"]:
            return {"valid": False, "error": validation_result.get("error", "Invalid token")}
        
        return validation_result
    except Exception as e:
        return {"valid": False, "error": f"Token validation failed: {str(e)}"}