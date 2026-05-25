from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List

from config.base_datos import obtener_db
from config.dependencias import propietario_actual
from esquemas.contrato import ContratoCrear, ContratoActualizar, ContratoRespuesta
from modelos.propietario import Propietario
import controladores.controlador_contrato as ctrl

enrutador = APIRouter(prefix="/contratos", tags=["Contratos"])


@enrutador.post("/", response_model=ContratoRespuesta, status_code=status.HTTP_201_CREATED)
async def crear_contrato(
    datos: ContratoCrear,
    db: Session = Depends(obtener_db),
    _: Propietario = Depends(propietario_actual)
):
    """Crear un nuevo contrato y generar pagos mensuales automáticamente"""
    return ctrl.crear(db, datos)


@enrutador.get("/", response_model=List[ContratoRespuesta])
async def listar_contratos(
    saltar: int = 0,
    limite: int = 100,
    db: Session = Depends(obtener_db),
    _: Propietario = Depends(propietario_actual)
):
    """Listar todos los contratos"""
    return ctrl.obtener_todos(db, saltar, limite)


@enrutador.get("/por_vencer", response_model=List[ContratoRespuesta])
async def contratos_por_vencer(
    dias: int = 30,
    db: Session = Depends(obtener_db),
    _: Propietario = Depends(propietario_actual)
):
    """Listar contratos próximos a vencer"""
    return ctrl.obtener_por_vencer(db, dias)


@enrutador.get("/{contrato_id}", response_model=ContratoRespuesta)
async def obtener_contrato(
    contrato_id: int,
    db: Session = Depends(obtener_db),
    _: Propietario = Depends(propietario_actual)
):
    """Obtener un contrato por ID"""
    return ctrl.obtener_por_id(db, contrato_id)


@enrutador.put("/{contrato_id}", response_model=ContratoRespuesta)
async def actualizar_contrato(
    contrato_id: int,
    datos: ContratoActualizar,
    db: Session = Depends(obtener_db),
    _: Propietario = Depends(propietario_actual)
):
    """Actualizar datos de un contrato"""
    return ctrl.actualizar(db, contrato_id, datos)


@enrutador.put("/{contrato_id}/finalizar", response_model=ContratoRespuesta)
async def finalizar_contrato(
    contrato_id: int,
    db: Session = Depends(obtener_db),
    _: Propietario = Depends(propietario_actual)
):
    """Finalizar un contrato y liberar la habitación"""
    return ctrl.finalizar(db, contrato_id)