from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional


class PropietarioBase(BaseModel):
    nombre: str
    correo: EmailStr
    telefono: Optional[str] = None
    dni: str


class PropietarioCrear(PropietarioBase):
    contrasena: str


class PropietarioActualizar(BaseModel):
    nombre: Optional[str] = None
    correo: Optional[EmailStr] = None
    telefono: Optional[str] = None
    contrasena: Optional[str] = None


class PropietarioRespuesta(PropietarioBase):
    id: int
    activo: bool
    creado_en: datetime

    class Config:
        from_attributes = True


class PropietarioLogin(BaseModel):
    correo: EmailStr
    contrasena: str