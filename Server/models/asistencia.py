from pydantic import BaseModel
from datetime import datetime

class RegistroAsistencia(BaseModel):
    uid: str
    nombre_aula: str

class AsistenciaResponse(BaseModel):
    mensaje: str
    usuario_id: int
    aula_id: int
    fecha_hora: datetime