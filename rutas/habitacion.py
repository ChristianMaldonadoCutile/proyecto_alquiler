from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List

from config.base_datos import obtener_db
from config.dependencias import propietario_actual
from esquemas.habitacion import HabitacionCrear, HabitacionActualizar, HabitacionRespuesta
from modelos.propietario import Propietario
import controladores.controlador_habitacion as ctrl

enrutador = APIRouter(prefix="/habitaciones", tags=["Habitaciones"])


@enrutador.post("/", response_model=HabitacionRespuesta, status_code=status.HTTP_201_CREATED)
async def crear_habitacion(
    datos: HabitacionCrear,
    db: Session = Depends(obtener_db),
    _: Propietario = Depends(propietario_actual)
):
    """Registrar una nueva habitación"""
    return ctrl.crear(db, datos)


@enrutador.get("/", response_model=List[HabitacionRespuesta])
async def listar_habitaciones(
    saltar: int = 0,
    limite: int = 100,
    db: Session = Depends(obtener_db),
    _: Propietario = Depends(propietario_actual)
):
    """Listar todas las habitaciones"""
    return ctrl.obtener_todas(db, saltar, limite)


@enrutador.get("/disponibles", response_model=List[HabitacionRespuesta])
async def listar_disponibles(
    db: Session = Depends(obtener_db),
    _: Propietario = Depends(propietario_actual)
):
    """Listar solo habitaciones disponibles"""
    return ctrl.obtener_disponibles(db)


@enrutador.get("/{habitacion_id}", response_model=HabitacionRespuesta)
async def obtener_habitacion(
    habitacion_id: int,
    db: Session = Depends(obtener_db),
    _: Propietario = Depends(propietario_actual)
):
    """Obtener una habitación por ID"""
    return ctrl.obtener_por_id(db, habitacion_id)


@enrutador.put("/{habitacion_id}", response_model=HabitacionRespuesta)
async def actualizar_habitacion(
    habitacion_id: int,
    datos: HabitacionActualizar,
    db: Session = Depends(obtener_db),
    _: Propietario = Depends(propietario_actual)
):
    """Actualizar datos de una habitación"""
    return ctrl.actualizar(db, habitacion_id, datos)


@enrutador.delete("/{habitacion_id}")
async def eliminar_habitacion(
    habitacion_id: int,
    db: Session = Depends(obtener_db),
    _: Propietario = Depends(propietario_actual)
):
    """Eliminar una habitación"""
    return ctrl.eliminar(db, habitacion_id)