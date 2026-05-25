from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from config.base_datos import Base


class EstadoHabitacion(str, enum.Enum):
    disponible = "disponible"
    ocupada = "ocupada"
    mantenimiento = "mantenimiento"


class Habitacion(Base):
    __tablename__ = "habitaciones"

    id = Column(Integer, primary_key=True, index=True)
    numero = Column(String(10), nullable=False)
    piso = Column(Integer, nullable=True)
    descripcion = Column(String(255), nullable=True)
    precio_mensual = Column(Float, nullable=False)
    estado = Column(Enum(EstadoHabitacion), default=EstadoHabitacion.disponible)
    propietario_id = Column(Integer, ForeignKey("propietarios.id"), nullable=False)
    creado_en = Column(DateTime(timezone=True), server_default=func.now())
    actualizado_en = Column(DateTime(timezone=True), onupdate=func.now())

    # Relaciones
    propietario = relationship("Propietario", back_populates="habitaciones")
    contratos = relationship("Contrato", back_populates="habitacion")