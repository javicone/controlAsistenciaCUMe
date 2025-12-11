from pydantic import BaseModel

class DatosAula(BaseModel):
    aula: str
    temperatura: float
    luz: float
    presion: float
    humedad: float
    personas: int
    clase_en_curso: bool

class ControlRelay(BaseModel):
    aula: str
    aerotermia: bool
    iluminacion: bool

class EstadoAula(BaseModel):
    temperatura: float
    humedad: float
    presion: float
    luz: float
    personas: int
    clase_en_curso: bool
    relay: bool