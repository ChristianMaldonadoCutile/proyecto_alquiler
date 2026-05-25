from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from modelos.habitacion import EstadoHabitacion


class HabitacionBase(BaseModel):
    numero: str
    piso: Optional[int] = None
    descripcion: Optional[str] = None
    precio_mensual: float
    propietario_id: int


class HabitacionCrear(HabitacionBase):
    pass


class HabitacionActualizar(BaseModel):
    numero: Optional[str] = None
    piso: Optional[int] = None
    descripcion: Optional[str] = None
    precio_mensual: Optional[float] = None
    estado: Optional[EstadoHabitacion] = None


class HabitacionRespuesta(HabitacionBase):
    id: int
    estado: EstadoHabitacion
    creado_en: datetime

    class Config:
        from_attributes = True