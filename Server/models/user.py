from pydantic import BaseModel, EmailStr

class UserLogin(BaseModel):
    correo: EmailStr
    password: str

class AulaLogin(BaseModel):
    nombre_aula: str
    password_aula: str

class TokenData(BaseModel):
    id: str | None = None
    rol: str | None = None

class UserInDB(BaseModel):
    id: int
    correo: str
    rol: str
    password: str