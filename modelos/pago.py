from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey, Enum, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from config.base_datos import Base


class EstadoPago(str, enum.Enum):
    pendiente = "pendiente"
    pagado = "pagado"
    vencido = "vencido"


class MetodoPago(str, enum.Enum):
    efectivo = "efectivo"
    transferencia = "transferencia"
    deposito = "deposito"


class Pago(Base):
    __tablename__ = "pagos"

    id = Column(Integer, primary_key=True, index=True)
    contrato_id = Column(Integer, ForeignKey("contratos.id"), nullable=False)
    monto = Column(Float, nullable=False)
    fecha_pago = Column(DateTime(timezone=True), nullable=True)
    fecha_vencimiento = Column(DateTime(timezone=True), nullable=False)
    estado = Column(Enum(EstadoPago), default=EstadoPago.pendiente)
    metodo = Column(Enum(MetodoPago), nullable=True)
    observacion = Column(String(255), nullable=True)
    creado_en = Column(DateTime(timezone=True), server_default=func.now())
    actualizado_en = Column(DateTime(timezone=True), onupdate=func.now())

    # Relaciones
    contrato = relationship("Contrato", back_populates="pagos")