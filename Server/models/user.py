from pydantic import BaseModel, EmailStr, constr, validator, Field
from typing import Optional
import re

class UserLogin(BaseModel):
    correo: EmailStr
    password: constr(min_length=8, max_length=100)
    
    @validator('correo')
    def email_lowercase(cls, v):
        """Normalizar email a minúsculas y validar formato"""
        email = v.lower().strip()
        # Prevenir inyección XSS en email
        dangerous_chars = ['<', '>', '"', "'", '\\', ';']
        if any(char in email for char in dangerous_chars):
            raise ValueError('Email contiene caracteres no permitidos')
        return email
    
    @validator('password')
    def password_not_common(cls, v):
        """Verificar que no sea una contraseña común (primera capa)"""
        common = ['12345678', 'password', 'qwerty', 'admin123', '00000000']
        if v.lower() in common:
            raise ValueError('Contraseña demasiado común')
        # Prevenir inyección SQL en password
        if any(pattern in v.lower() for pattern in ['--', ';', 'drop', 'union', 'select']):
            raise ValueError('Password contiene caracteres no permitidos')
        return v

class AulaLogin(BaseModel):
    nombre_aula: str
    password_aula: str

class TokenData(BaseModel):
    id: str | None = None
    rol: str | None = None

class UserInDB(BaseModel):
    id: int
    nombre: str
    correo: str
    rol: str
    password: str

    