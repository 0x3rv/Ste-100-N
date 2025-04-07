from pydantic import BaseModel

class UserCreate(BaseModel):
    email: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

class ForgotPassword(BaseModel):
    email: str

class UserResponse(BaseModel):
    email: str
    token: str


class SignupResponse(BaseModel):
    message: str
