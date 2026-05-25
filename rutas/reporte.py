from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime

from config.base_datos import obtener_db
from config.dependencias import propietario_actual
from modelos.propietario import Propietario
import controladores.controlador_reporte as ctrl

enrutador = APIRouter(prefix="/reportes", tags=["Reportes"])


@enrutador.get("/resumen")
async def resumen_general(
    db: Session = Depends(obtener_db),
    _: Propietario = Depends(propietario_actual)
):
    """Resumen general del sistema — ingresos, deudas y ocupación"""
    return ctrl.reporte_resumen(db)


@enrutador.get("/ingresos")
async def ingresos_por_periodo(
    fecha_inicio: datetime,
    fecha_fin: datetime,
    db: Session = Depends(obtener_db),
    _: Propietario = Depends(propietario_actual)
):
    """Ingresos cobrados en un rango de fechas"""
    return ctrl.reporte_ingresos(db, fecha_inicio, fecha_fin)


@enrutador.get("/ocupacion")
async def tasa_ocupacion(
    db: Session = Depends(obtener_db),
    _: Propietario = Depends(propietario_actual)
):
    """Tasa de ocupación de habitaciones"""
    return ctrl.reporte_ocupacion(db)


@enrutador.get("/deudores")
async def reporte_deudores(
    db: Session = Depends(obtener_db),
    _: Propietario = Depends(propietario_actual)
):
    """Reporte completo de inquilinos con deuda"""
    return ctrl.reporte_deudores(db)