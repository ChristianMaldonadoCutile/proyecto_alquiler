from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from modelos.contrato import EstadoContrato


class ContratoBase(BaseModel):
    habitacion_id: int
    inquilino_id: int
    fecha_inicio: datetime
    fecha_fin: datetime
    monto_mensual: float
    dia_vencimiento: Optional[int] = 1


class ContratoCrear(ContratoBase):
    pass


class ContratoActualizar(BaseModel):
    fecha_fin: Optional[datetime] = None
    monto_mensual: Optional[float] = None
    dia_vencimiento: Optional[int] = None
    estado: Optional[EstadoContrato] = None


class ContratoRespuesta(ContratoBase):
    id: int
    estado: EstadoContrato
    creado_en: datetime

    class Config:
        from_attributes = True