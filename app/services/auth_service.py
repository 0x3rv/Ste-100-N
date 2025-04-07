from passlib.context import CryptContext
from fastapi import HTTPException
from app.models.user import users_collection
from app.utils.jwt_handler import create_jwt
from app.utils.email_handler import send_verification_email  # Assume this is implemented
from pymongo.errors import DuplicateKeyError
import uuid
from app.utils.jwt_handler import decode_jwt
from jose import jwt
from jose.exceptions import JWTError, ExpiredSignatureError, JWTClaimsError, JWSError

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def register_user(email: str, password: str):
    user = await users_collection.find_one({"email": email})
    if user:
        raise HTTPException(status_code=400, detail="User already exists")

    hashed_pw = pwd_context.hash(password)
    verification_code = str(uuid.uuid4())  # Generate a unique verification code
    await users_collection.insert_one({
        "email": email,
        "password": hashed_pw,
        "is_verified": False,
        "verification_code": verification_code
    })

    # Send verification email
    verification_link = f"http://yourdomain.com/verify?code={verification_code}"
    await send_verification_email(email, verification_link)

    return {"message": "Registration successful. Please verify your email."}

async def login_user(email: str, password: str):
    user = await users_collection.find_one({"email": email})
    if not user or not pwd_context.verify(password, user["password"]):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    if not user.get("is_verified"):
        raise HTTPException(status_code=400, detail="Email not verified. Please check your email.")

    token = create_jwt(email)
    return {"email": email, "token": token}

async def verify_user(verification_code: str):
    user = await users_collection.find_one({"verification_code": verification_code})
    if not user:
        raise HTTPException(status_code=400, detail="Invalid verification code")

    await users_collection.update_one(
        {"verification_code": verification_code},
        {"$set": {"is_verified": True}, "$unset": {"verification_code": ""}}
    )

    return {"message": "Email verified successfully."}




async def validate_token_service(token: str):
    try:
        if not isinstance(token, str) or not token.strip():
            return {"valid": False, "error": "Token must be a non-empty string"}
            
        # Basic token format validation
        if len(token.split('.')) != 3:
            return {"valid": False, "error": "Invalid token format"}
            
        decoded_token = decode_jwt(token)
        return {"email": decoded_token.get("email"), "valid": True}
    except (UnicodeDecodeError, ValueError) as e:
        return {"valid": False, "error": "Malformed token"}
    except (JWTError, JWSError, ExpiredSignatureError, JWTClaimsError) as e:
        return {"valid": False, "error": str(e)}
    except Exception as e:
        return {"valid": False, "error": f"Token validation failed: {str(e)}"}

