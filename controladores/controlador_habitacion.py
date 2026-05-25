from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from modelos.habitacion import Habitacion, EstadoHabitacion
from esquemas.habitacion import HabitacionCrear, HabitacionActualizar


def obtener_todas(db: Session, saltar: int = 0, limite: int = 100):
    return db.query(Habitacion).offset(saltar).limit(limite).all()


def obtener_disponibles(db: Session):
    return db.query(Habitacion).filter(
        Habitacion.estado == EstadoHabitacion.disponible
    ).all()


def obtener_por_id(db: Session, habitacion_id: int):
    habitacion = db.query(Habitacion).filter(Habitacion.id == habitacion_id).first()
    if not habitacion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Habitación con id {habitacion_id} no encontrada"
        )
    return habitacion


def crear(db: Session, datos: HabitacionCrear):
    existente = db.query(Habitacion).filter(
        Habitacion.numero == datos.numero,
        Habitacion.propietario_id == datos.propietario_id
    ).first()
    if existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ya existe una habitación con el número {datos.numero} para este propietario"
        )
    nueva = Habitacion(**datos.model_dump())
    db.add(nueva)
    db.commit()
    db.refresh(nueva)
    return nueva


def actualizar(db: Session, habitacion_id: int, datos: HabitacionActualizar):
    habitacion = obtener_por_id(db, habitacion_id)
    datos_actualizar = datos.model_dump(exclude_unset=True)
    for campo, valor in datos_actualizar.items():
        setattr(habitacion, campo, valor)
    db.commit()
    db.refresh(habitacion)
    return habitacion


def eliminar(db: Session, habitacion_id: int):
    habitacion = obtener_por_id(db, habitacion_id)
    if habitacion.estado == EstadoHabitacion.ocupada:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se puede eliminar una habitación ocupada"
        )
    db.delete(habitacion)
    db.commit()
    return {"mensaje": "Habitación eliminada correctamente"}