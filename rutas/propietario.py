from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List

from config.base_datos import obtener_db
from config.dependencias import propietario_actual
from esquemas.propietario import PropietarioCrear, PropietarioActualizar, PropietarioRespuesta
from esquemas.token import Token
from modelos.propietario import Propietario
import controladores.controlador_propietario as ctrl

enrutador = APIRouter(prefix="/propietarios", tags=["Propietarios"])


@enrutador.post("/login", response_model=Token)
async def iniciar_sesion(
    formulario: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(obtener_db)
):
    """Iniciar sesión con correo y contraseña"""
    return ctrl.autenticar(db, formulario.username, formulario.password)


@enrutador.post("/", response_model=PropietarioRespuesta, status_code=status.HTTP_201_CREATED)
async def crear_propietario(
    datos: PropietarioCrear,
    db: Session = Depends(obtener_db)
):
    """Registrar un nuevo propietario"""
    return ctrl.crear(db, datos)


@enrutador.get("/yo", response_model=PropietarioRespuesta)
async def obtener_yo(actual: Propietario = Depends(propietario_actual)):
    """Obtener el propietario autenticado"""
    return actual


@enrutador.get("/", response_model=List[PropietarioRespuesta])
async def listar_propietarios(
    saltar: int = 0,
    limite: int = 100,
    db: Session = Depends(obtener_db),
    _: Propietario = Depends(propietario_actual)
):
    """Listar todos los propietarios"""
    return ctrl.obtener_todos(db, saltar, limite)


@enrutador.get("/{propietario_id}", response_model=PropietarioRespuesta)
async def obtener_propietario(
    propietario_id: int,
    db: Session = Depends(obtener_db),
    _: Propietario = Depends(propietario_actual)
):
    """Obtener un propietario por ID"""
    return ctrl.obtener_por_id(db, propietario_id)


@enrutador.put("/{propietario_id}", response_model=PropietarioRespuesta)
async def actualizar_propietario(
    propietario_id: int,
    datos: PropietarioActualizar,
    db: Session = Depends(obtener_db),
    _: Propietario = Depends(propietario_actual)
):
    """Actualizar datos de un propietario"""
    return ctrl.actualizar(db, propietario_id, datos)


@enrutador.delete("/{propietario_id}")
async def eliminar_propietario(
    propietario_id: int,
    db: Session = Depends(obtener_db),
    _: Propietario = Depends(propietario_actual)
):
    """Dar de baja un propietario"""
    return ctrl.eliminar(db, propietario_id)