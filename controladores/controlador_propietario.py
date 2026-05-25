from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from passlib.context import CryptContext
from jose import jwt, JWTError
from datetime import datetime, timedelta

from modelos.propietario import Propietario
from esquemas.propietario import PropietarioCrear, PropietarioActualizar
from config.base_datos import configuracion

cifrado = CryptContext(schemes=["bcrypt"])


def obtener_todos(db: Session, saltar: int = 0, limite: int = 100):
    return db.query(Propietario).filter(Propietario.activo == True).offset(saltar).limit(limite).all()


def obtener_por_id(db: Session, propietario_id: int):
    propietario = db.query(Propietario).filter(
        Propietario.id == propietario_id,
        Propietario.activo == True
    ).first()
    if not propietario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Propietario con id {propietario_id} no encontrado"
        )
    return propietario


def obtener_por_correo(db: Session, correo: str):
    return db.query(Propietario).filter(Propietario.correo == correo).first()


def crear(db: Session, datos: PropietarioCrear):
    if obtener_por_correo(db, datos.correo):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe un propietario con ese correo"
        )
    contrasena_hash = cifrado.hash(datos.contrasena)
    nuevo = Propietario(
        nombre=datos.nombre,
        correo=datos.correo,
        telefono=datos.telefono,
        dni=datos.dni,
        contrasena_hash=contrasena_hash
    )
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo


def actualizar(db: Session, propietario_id: int, datos: PropietarioActualizar):
    propietario = obtener_por_id(db, propietario_id)
    datos_actualizar = datos.model_dump(exclude_unset=True)
    if "contrasena" in datos_actualizar:
        datos_actualizar["contrasena_hash"] = cifrado.hash(datos_actualizar.pop("contrasena"))
    for campo, valor in datos_actualizar.items():
        setattr(propietario, campo, valor)
    db.commit()
    db.refresh(propietario)
    return propietario


def eliminar(db: Session, propietario_id: int):
    propietario = obtener_por_id(db, propietario_id)
    propietario.activo = False
    db.commit()
    return {"mensaje": "Propietario eliminado correctamente"}


def autenticar(db: Session, correo: str, contrasena: str):
    propietario = obtener_por_correo(db, correo)
    if not propietario or not cifrado.verify(contrasena, propietario.contrasena_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Correo o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    expiracion = datetime.utcnow() + timedelta(minutes=configuracion.DURACION_TOKEN_MINUTOS)
    token = jwt.encode(
        {"sub": propietario.correo, "exp": expiracion},
        configuracion.CLAVE_SECRETA,
        algorithm=configuracion.ALGORITMO
    )
    return {"access_token": token, "token_type": "bearer"}


def obtener_propietario_actual(db: Session, token: str):
    excepcion = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudo validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, configuracion.CLAVE_SECRETA, algorithms=[configuracion.ALGORITMO])
        correo: str = payload.get("sub")
        if correo is None:
            raise excepcion
    except JWTError:
        raise excepcion
    propietario = obtener_por_correo(db, correo)
    if propietario is None:
        raise excepcion
    return propietario