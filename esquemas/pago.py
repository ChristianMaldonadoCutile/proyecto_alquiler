from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from modelos.pago import EstadoPago, MetodoPago


class PagoBase(BaseModel):
    contrato_id: int
    monto: float
    fecha_vencimiento: datetime
    observacion: Optional[str] = None


class PagoCrear(PagoBase):
    pass


class PagoActualizar(BaseModel):
    monto: Optional[float] = None
    fecha_pago: Optional[datetime] = None
    fecha_vencimiento: Optional[datetime] = None
    estado: Optional[EstadoPago] = None
    metodo: Optional[MetodoPago] = None
    observacion: Optional[str] = None


class PagoRegistrar(BaseModel):
    metodo: MetodoPago
    observacion: Optional[str] = None


class PagoRespuesta(PagoBase):
    id: int
    fecha_pago: Optional[datetime] = None
    estado: EstadoPago
    metodo: Optional[MetodoPago] = None
    creado_en: datetime

    class Config:
        from_attributes = True