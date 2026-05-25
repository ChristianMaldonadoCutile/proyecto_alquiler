from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from datetime import datetime

from modelos.pago import Pago, EstadoPago
from modelos.contrato import Contrato
from esquemas.pago import PagoCrear, PagoActualizar, PagoRegistrar


def obtener_todos(db: Session, saltar: int = 0, limite: int = 100):
    return db.query(Pago).offset(saltar).limit(limite).all()


def obtener_por_id(db: Session, pago_id: int):
    pago = db.query(Pago).filter(Pago.id == pago_id).first()
    if not pago:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Pago con id {pago_id} no encontrado"
        )
    return pago


def obtener_pendientes(db: Session):
    return db.query(Pago).filter(
        Pago.estado == EstadoPago.pendiente
    ).all()


def obtener_vencidos(db: Session):
    ahora = datetime.utcnow()
    # Actualizar pagos vencidos automáticamente
    db.query(Pago).filter(
        Pago.estado == EstadoPago.pendiente,
        Pago.fecha_vencimiento < ahora
    ).update({"estado": EstadoPago.vencido})
    db.commit()
    return db.query(Pago).filter(
        Pago.estado == EstadoPago.vencido
    ).all()


def obtener_por_contrato(db: Session, contrato_id: int):
    return db.query(Pago).filter(
        Pago.contrato_id == contrato_id
    ).all()


def crear(db: Session, datos: PagoCrear):
    contrato = db.query(Contrato).filter(
        Contrato.id == datos.contrato_id
    ).first()
    if not contrato:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contrato no encontrado"
        )
    nuevo = Pago(**datos.model_dump())
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo


def registrar_pago(db: Session, pago_id: int, datos: PagoRegistrar):
    pago = obtener_por_id(db, pago_id)
    if pago.estado == EstadoPago.pagado:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Este pago ya fue registrado"
        )
    pago.estado = EstadoPago.pagado
    pago.fecha_pago = datetime.utcnow()
    pago.metodo = datos.metodo
    pago.observacion = datos.observacion
    db.commit()
    db.refresh(pago)
    return pago


def actualizar(db: Session, pago_id: int, datos: PagoActualizar):
    pago = obtener_por_id(db, pago_id)
    datos_actualizar = datos.model_dump(exclude_unset=True)
    for campo, valor in datos_actualizar.items():
        setattr(pago, campo, valor)
    db.commit()
    db.refresh(pago)
    return pago


def obtener_deudores(db: Session):
    pagos_vencidos = db.query(Pago).filter(
        Pago.estado == EstadoPago.vencido
    ).all()
    deudores = {}
    for pago in pagos_vencidos:
        contrato = db.query(Contrato).filter(
            Contrato.id == pago.contrato_id
        ).first()
        if contrato:
            inquilino_id = contrato.inquilino_id
            if inquilino_id not in deudores:
                deudores[inquilino_id] = {
                    "inquilino_id": inquilino_id,
                    "total_deuda": 0,
                    "pagos_vencidos": 0
                }
            deudores[inquilino_id]["total_deuda"] += pago.monto
            deudores[inquilino_id]["pagos_vencidos"] += 1
    return list(deudores.values())