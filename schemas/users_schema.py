from pydantic import BaseModel, EmailStr, SecretStr


class UserRegisterRequestSchema(BaseModel):
    email: EmailStr
    password: SecretStr


class UserLoginRequestSchema(BaseModel):
    email: EmailStr
    password: SecretStr
