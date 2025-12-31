from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class RegistroAsistencia(BaseModel):
    uid: str
    device_id: str
    timestamp: Optional[datetime] = Field(default=None, description="Timestamp del fichaje (opcional, se usa el del servidor si no se proporciona)")

class AsistenciaResponse(BaseModel):
    mensaje: str
    usuario_id: int
    aula_id: int
    clase_id: Optional[int] = None
    asignatura: Optional[str] = None
    fecha_hora: datetime