from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional


class InquilinoBase(BaseModel):
    nombre: str
    correo: EmailStr
    telefono: Optional[str] = None
    dni: str
    contacto_emergencia: Optional[str] = None
    telefono_emergencia: Optional[str] = None


class InquilinoCrear(InquilinoBase):
    contrasena: str


class InquilinoActualizar(BaseModel):
    nombre: Optional[str] = None
    correo: Optional[EmailStr] = None
    telefono: Optional[str] = None
    contacto_emergencia: Optional[str] = None
    telefono_emergencia: Optional[str] = None
    contrasena: Optional[str] = None


class InquilinoRespuesta(InquilinoBase):
    id: int
    activo: bool
    creado_en: datetime

    class Config:
        from_attributes = True