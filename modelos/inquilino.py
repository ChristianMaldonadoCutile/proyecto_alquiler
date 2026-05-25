from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from config.base_datos import Base


class Inquilino(Base):
    __tablename__ = "inquilinos"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    correo = Column(String(100), unique=True, index=True, nullable=False)
    telefono = Column(String(20), nullable=True)
    dni = Column(String(20), unique=True, nullable=False)
    contacto_emergencia = Column(String(100), nullable=True)
    telefono_emergencia = Column(String(20), nullable=True)
    contrasena_hash = Column(String(255), nullable=True)
    activo = Column(Boolean, default=True)
    creado_en = Column(DateTime(timezone=True), server_default=func.now())
    actualizado_en = Column(DateTime(timezone=True), onupdate=func.now())

    # Relaciones
    contratos = relationship("Contrato", back_populates="inquilino")