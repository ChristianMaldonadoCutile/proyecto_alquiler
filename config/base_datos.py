from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pydantic_settings import BaseSettings


class Configuracion(BaseSettings):
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "contraseña"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: str = "5432"
    POSTGRES_DB: str = "sistema_alquiler"
    CLAVE_SECRETA: str = "clave_secreta_cambiar_en_produccion"
    ALGORITMO: str = "HS256"
    DURACION_TOKEN_MINUTOS: int = 60

    @property
    def url_base_datos(self) -> str:
        return (
            f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    class Config:
        env_file = ".env"


configuracion = Configuracion()

motor = create_engine(configuracion.url_base_datos)

SesionLocal = sessionmaker(autocommit=False, autoflush=False, bind=motor)

Base = declarative_base()


def obtener_db():
    db = SesionLocal()
    try:
        yield db
    finally:
        db.close()