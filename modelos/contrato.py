from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from config.base_datos import Base


class EstadoContrato(str, enum.Enum):
    activo = "activo"
    finalizado = "finalizado"
    cancelado = "cancelado"


class Contrato(Base):
    __tablename__ = "contratos"

    id = Column(Integer, primary_key=True, index=True)
    habitacion_id = Column(Integer, ForeignKey("habitaciones.id"), nullable=False)
    inquilino_id = Column(Integer, ForeignKey("inquilinos.id"), nullable=False)
    fecha_inicio = Column(DateTime(timezone=True), nullable=False)
    fecha_fin = Column(DateTime(timezone=True), nullable=False)
    monto_mensual = Column(Float, nullable=False)
    dia_vencimiento = Column(Integer, default=1)
    estado = Column(Enum(EstadoContrato), default=EstadoContrato.activo)
    creado_en = Column(DateTime(timezone=True), server_default=func.now())
    actualizado_en = Column(DateTime(timezone=True), onupdate=func.now())

    # Relaciones
    habitacion = relationship("Habitacion", back_populates="contratos")
    inquilino = relationship("Inquilino", back_populates="contratos")
    pagos = relationship("Pago", back_populates="contrato")