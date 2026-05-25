from fastapi import APIRouter, Depends, status
from fastapi.responses import Response
from sqlalchemy.orm import Session
from typing import List

from config.base_datos import obtener_db
from config.dependencias import propietario_actual
from esquemas.pago import PagoCrear, PagoActualizar, PagoRespuesta, PagoRegistrar
from modelos.propietario import Propietario
from modelos.contrato import Contrato
from modelos.inquilino import Inquilino
from modelos.habitacion import Habitacion
from servicios.servicio_recibo import generar_recibo
import controladores.controlador_pago as ctrl

enrutador = APIRouter(prefix="/pagos", tags=["Pagos"])


@enrutador.post("/", response_model=PagoRespuesta, status_code=status.HTTP_201_CREATED)
async def crear_pago(
    datos: PagoCrear,
    db: Session = Depends(obtener_db),
    _: Propietario = Depends(propietario_actual)
):
    """Crear un pago manual"""
    return ctrl.crear(db, datos)


@enrutador.get("/", response_model=List[PagoRespuesta])
async def listar_pagos(
    saltar: int = 0,
    limite: int = 100,
    db: Session = Depends(obtener_db),
    _: Propietario = Depends(propietario_actual)
):
    """Listar todos los pagos"""
    return ctrl.obtener_todos(db, saltar, limite)


@enrutador.get("/pendientes", response_model=List[PagoRespuesta])
async def pagos_pendientes(
    db: Session = Depends(obtener_db),
    _: Propietario = Depends(propietario_actual)
):
    """Listar pagos pendientes"""
    return ctrl.obtener_pendientes(db)


@enrutador.get("/vencidos", response_model=List[PagoRespuesta])
async def pagos_vencidos(
    db: Session = Depends(obtener_db),
    _: Propietario = Depends(propietario_actual)
):
    """Listar pagos vencidos"""
    return ctrl.obtener_vencidos(db)


@enrutador.get("/deudores")
async def listar_deudores(
    db: Session = Depends(obtener_db),
    _: Propietario = Depends(propietario_actual)
):
    """Listar inquilinos con deuda"""
    return ctrl.obtener_deudores(db)


@enrutador.get("/contrato/{contrato_id}", response_model=List[PagoRespuesta])
async def pagos_por_contrato(
    contrato_id: int,
    db: Session = Depends(obtener_db),
    _: Propietario = Depends(propietario_actual)
):
    """Listar todos los pagos de un contrato"""
    return ctrl.obtener_por_contrato(db, contrato_id)


@enrutador.get("/{pago_id}", response_model=PagoRespuesta)
async def obtener_pago(
    pago_id: int,
    db: Session = Depends(obtener_db),
    _: Propietario = Depends(propietario_actual)
):
    """Obtener un pago por ID"""
    return ctrl.obtener_por_id(db, pago_id)


@enrutador.put("/{pago_id}/registrar", response_model=PagoRespuesta)
async def registrar_pago(
    pago_id: int,
    datos: PagoRegistrar,
    db: Session = Depends(obtener_db),
    _: Propietario = Depends(propietario_actual)
):
    """Registrar un pago como pagado"""
    return ctrl.registrar_pago(db, pago_id, datos)


@enrutador.get("/{pago_id}/recibo")
async def descargar_recibo(
    pago_id: int,
    db: Session = Depends(obtener_db),
    _: Propietario = Depends(propietario_actual)
):
    """Generar y descargar recibo PDF de un pago"""
    pago = ctrl.obtener_por_id(db, pago_id)
    contrato = db.query(Contrato).filter(Contrato.id == pago.contrato_id).first()
    inquilino = db.query(Inquilino).filter(Inquilino.id == contrato.inquilino_id).first()
    habitacion = db.query(Habitacion).filter(Habitacion.id == contrato.habitacion_id).first()

    pdf = generar_recibo(pago, contrato, inquilino, habitacion)

    return Response(
        content=pdf,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=recibo_pago_{pago_id:04d}.pdf"
        }
    )


@enrutador.put("/{pago_id}", response_model=PagoRespuesta)
async def actualizar_pago(
    pago_id: int,
    datos: PagoActualizar,
    db: Session = Depends(obtener_db),
    _: Propietario = Depends(propietario_actual)
):
    """Actualizar datos de un pago"""
    return ctrl.actualizar(db, pago_id, datos)