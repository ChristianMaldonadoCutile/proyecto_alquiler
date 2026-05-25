from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List

from config.base_datos import obtener_db
from config.dependencias import propietario_actual
from esquemas.inquilino import InquilinoCrear, InquilinoActualizar, InquilinoRespuesta
from modelos.propietario import Propietario
import controladores.controlador_inquilino as ctrl

enrutador = APIRouter(prefix="/inquilinos", tags=["Inquilinos"])


@enrutador.post("/", response_model=InquilinoRespuesta, status_code=status.HTTP_201_CREATED)
async def crear_inquilino(
    datos: InquilinoCrear,
    db: Session = Depends(obtener_db),
    _: Propietario = Depends(propietario_actual)
):
    """Registrar un nuevo inquilino"""
    return ctrl.crear(db, datos)


@enrutador.get("/", response_model=List[InquilinoRespuesta])
async def listar_inquilinos(
    saltar: int = 0,
    limite: int = 100,
    db: Session = Depends(obtener_db),
    _: Propietario = Depends(propietario_actual)
):
    """Listar todos los inquilinos activos"""
    return ctrl.obtener_todos(db, saltar, limite)


@enrutador.get("/{inquilino_id}", response_model=InquilinoRespuesta)
async def obtener_inquilino(
    inquilino_id: int,
    db: Session = Depends(obtener_db),
    _: Propietario = Depends(propietario_actual)
):
    """Obtener un inquilino por ID"""
    return ctrl.obtener_por_id(db, inquilino_id)


@enrutador.put("/{inquilino_id}", response_model=InquilinoRespuesta)
async def actualizar_inquilino(
    inquilino_id: int,
    datos: InquilinoActualizar,
    db: Session = Depends(obtener_db),
    _: Propietario = Depends(propietario_actual)
):
    """Actualizar datos de un inquilino"""
    return ctrl.actualizar(db, inquilino_id, datos)


@enrutador.delete("/{inquilino_id}")
async def dar_baja_inquilino(
    inquilino_id: int,
    db: Session = Depends(obtener_db),
    _: Propietario = Depends(propietario_actual)
):
    """Dar de baja a un inquilino"""
    return ctrl.eliminar(db, inquilino_id)