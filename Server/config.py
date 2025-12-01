DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '1234',
    'database': 'control-asistencia'
}

SECRET_KEY = "asdfghjklñzxcvbnmQWERTYUIOPZXCVBNMLKJHGFDSA1234567890"
# --- Seguridad con JWT ---
ALGORITHM = "HS256"  # ✅ Cambiar de RS256 a HS256
ACCESS_TOKEN_EXPIRE_MINUTES = 1440  # 24 horas