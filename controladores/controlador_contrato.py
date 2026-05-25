from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from datetime import datetime, timedelta

from modelos.contrato import Contrato, EstadoContrato
from modelos.habitacion import Habitacion, EstadoHabitacion
from modelos.pago import Pago, EstadoPago
from esquemas.contrato import ContratoCrear, ContratoActualizar


def obtener_todos(db: Session, saltar: int = 0, limite: int = 100):
    return db.query(Contrato).offset(saltar).limit(limite).all()


def obtener_por_id(db: Session, contrato_id: int):
    contrato = db.query(Contrato).filter(Contrato.id == contrato_id).first()
    if not contrato:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Contrato con id {contrato_id} no encontrado"
        )
    return contrato


def obtener_por_vencer(db: Session, dias: int = 30):
    limite = datetime.utcnow() + timedelta(days=dias)
    return db.query(Contrato).filter(
        Contrato.estado == EstadoContrato.activo,
        Contrato.fecha_fin <= limite
    ).all()


def crear(db: Session, datos: ContratoCrear):
    # Verificar que la habitación esté disponible
    habitacion = db.query(Habitacion).filter(
        Habitacion.id == datos.habitacion_id
    ).first()
    if not habitacion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Habitación no encontrada"
        )
    if habitacion.estado != EstadoHabitacion.disponible:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La habitación no está disponible"
        )

    # Verificar que el inquilino no tenga contrato activo
    contrato_activo = db.query(Contrato).filter(
        Contrato.inquilino_id == datos.inquilino_id,
        Contrato.estado == EstadoContrato.activo
    ).first()
    if contrato_activo:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El inquilino ya tiene un contrato activo"
        )

    # Crear contrato
    nuevo = Contrato(**datos.model_dump())
    db.add(nuevo)

    # Cambiar estado de la habitación a ocupada
    habitacion.estado = EstadoHabitacion.ocupada

    # Generar pagos mensuales automáticamente
    fecha_actual = datos.fecha_inicio
    while fecha_actual < datos.fecha_fin:
        vencimiento = fecha_actual.replace(day=datos.dia_vencimiento)
        pago = Pago(
            contrato=nuevo,
            monto=datos.monto_mensual,
            fecha_vencimiento=vencimiento,
            estado=EstadoPago.pendiente
        )
        db.add(pago)
        # Avanzar al siguiente mes
        if fecha_actual.month == 12:
            fecha_actual = fecha_actual.replace(year=fecha_actual.year + 1, month=1)
        else:
            fecha_actual = fecha_actual.replace(month=fecha_actual.month + 1)

    db.commit()
    db.refresh(nuevo)
    return nuevo


def actualizar(db: Session, contrato_id: int, datos: ContratoActualizar):
    contrato = obtener_por_id(db, contrato_id)
    datos_actualizar = datos.model_dump(exclude_unset=True)
    for campo, valor in datos_actualizar.items():
        setattr(contrato, campo, valor)
    db.commit()
    db.refresh(contrato)
    return contrato


def finalizar(db: Session, contrato_id: int):
    contrato = obtener_por_id(db, contrato_id)
    if contrato.estado != EstadoContrato.activo:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El contrato no está activo"
        )
    # Finalizar contrato
    contrato.estado = EstadoContrato.finalizado

    # Liberar habitación
    habitacion = db.query(Habitacion).filter(
        Habitacion.id == contrato.habitacion_id
    ).first()
    if habitacion:
        habitacion.estado = EstadoHabitacion.disponible

    # Cancelar pagos pendientes
    db.query(Pago).filter(
        Pago.contrato_id == contrato_id,
        Pago.estado == EstadoPago.pendiente
    ).update({"estado": EstadoPago.vencido})

    db.commit()
    db.refresh(contrato)
    return contrato