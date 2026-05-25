from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from config.base_datos import Base


class Propietario(Base):
    __tablename__ = "propietarios"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    correo = Column(String(100), unique=True, index=True, nullable=False)
    telefono = Column(String(20), nullable=True)
    dni = Column(String(20), unique=True, nullable=False)
    contrasena_hash = Column(String(255), nullable=False)
    activo = Column(Boolean, default=True)
    creado_en = Column(DateTime(timezone=True), server_default=func.now())
    actualizado_en = Column(DateTime(timezone=True), onupdate=func.now())

    # Relaciones
    habitaciones = relationship("Habitacion", back_populates="propietario")