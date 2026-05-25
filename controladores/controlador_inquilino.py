from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from passlib.context import CryptContext
from jose import jwt, JWTError
from datetime import datetime, timedelta

from modelos.inquilino import Inquilino
from esquemas.inquilino import InquilinoCrear, InquilinoActualizar
from config.base_datos import configuracion

cifrado = CryptContext(schemes=["bcrypt"])


def obtener_todos(db: Session, saltar: int = 0, limite: int = 100):
    return db.query(Inquilino).filter(Inquilino.activo == True).offset(saltar).limit(limite).all()


def obtener_por_id(db: Session, inquilino_id: int):
    inquilino = db.query(Inquilino).filter(
        Inquilino.id == inquilino_id,
        Inquilino.activo == True
    ).first()
    if not inquilino:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Inquilino con id {inquilino_id} no encontrado"
        )
    return inquilino


def obtener_por_correo(db: Session, correo: str):
    return db.query(Inquilino).filter(Inquilino.correo == correo).first()


def obtener_por_dni(db: Session, dni: str):
    return db.query(Inquilino).filter(Inquilino.dni == dni).first()


def crear(db: Session, datos: InquilinoCrear):
    if obtener_por_correo(db, datos.correo):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe un inquilino con ese correo"
        )
    if obtener_por_dni(db, datos.dni):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe un inquilino con ese DNI"
        )
    contrasena_hash = cifrado.hash(datos.contrasena)
    nuevo = Inquilino(
        nombre=datos.nombre,
        correo=datos.correo,
        telefono=datos.telefono,
        dni=datos.dni,
        contacto_emergencia=datos.contacto_emergencia,
        telefono_emergencia=datos.telefono_emergencia,
        contrasena_hash=contrasena_hash
    )
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo


def actualizar(db: Session, inquilino_id: int, datos: InquilinoActualizar):
    inquilino = obtener_por_id(db, inquilino_id)
    datos_actualizar = datos.model_dump(exclude_unset=True)
    if "contrasena" in datos_actualizar:
        datos_actualizar["contrasena_hash"] = cifrado.hash(datos_actualizar.pop("contrasena"))
    for campo, valor in datos_actualizar.items():
        setattr(inquilino, campo, valor)
    db.commit()
    db.refresh(inquilino)
    return inquilino


def eliminar(db: Session, inquilino_id: int):
    inquilino = obtener_por_id(db, inquilino_id)
    inquilino.activo = False
    db.commit()
    return {"mensaje": "Inquilino dado de baja correctamente"}


def autenticar(db: Session, correo: str, contrasena: str):
    inquilino = obtener_por_correo(db, correo)
    if not inquilino or not inquilino.contrasena_hash:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Correo o contraseña incorrectos"
        )
    if not cifrado.verify(contrasena, inquilino.contrasena_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Correo o contraseña incorrectos"
        )
    expiracion = datetime.utcnow() + timedelta(minutes=configuracion.DURACION_TOKEN_MINUTOS)
    token = jwt.encode(
        {"sub": inquilino.correo, "rol": "inquilino", "exp": expiracion},
        configuracion.CLAVE_SECRETA,
        algorithm=configuracion.ALGORITMO
    )
    return {"access_token": token, "token_type": "bearer"}


def obtener_inquilino_actual(db: Session, token: str):
    excepcion = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudo validar las credenciales"
    )
    try:
        payload = jwt.decode(token, configuracion.CLAVE_SECRETA, algorithms=[configuracion.ALGORITMO])
        correo: str = payload.get("sub")
        rol: str = payload.get("rol")
        if correo is None or rol != "inquilino":
            raise excepcion
    except JWTError:
        raise excepcion
    inquilino = obtener_por_correo(db, correo)
    if inquilino is None:
        raise excepcion
    return inquilino