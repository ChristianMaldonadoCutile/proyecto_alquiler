from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from config.base_datos import obtener_db
from controladores.controlador_propietario import obtener_propietario_actual

oauth2_esquema = OAuth2PasswordBearer(tokenUrl="propietarios/login")


def propietario_actual(
    token: str = Depends(oauth2_esquema),
    db: Session = Depends(obtener_db)
):
    return obtener_propietario_actual(db, token)
