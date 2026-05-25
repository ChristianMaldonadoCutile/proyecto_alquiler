from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime

from modelos.pago import Pago, EstadoPago
from modelos.contrato import Contrato, EstadoContrato
from modelos.habitacion import Habitacion, EstadoHabitacion
from modelos.inquilino import Inquilino


def reporte_ingresos(db: Session, fecha_inicio: datetime, fecha_fin: datetime):
    pagos = db.query(Pago).filter(
        Pago.estado == EstadoPago.pagado,
        Pago.fecha_pago >= fecha_inicio,
        Pago.fecha_pago <= fecha_fin
    ).all()

    total = sum(p.monto for p in pagos)

    return {
        "fecha_inicio": fecha_inicio.strftime("%d/%m/%Y"),
        "fecha_fin": fecha_fin.strftime("%d/%m/%Y"),
        "total_ingresos": round(total, 2),
        "cantidad_pagos": len(pagos),
        "promedio_por_pago": round(total / len(pagos), 2) if pagos else 0,
        "detalle": [
            {
                "pago_id": p.id,
                "contrato_id": p.contrato_id,
                "monto": p.monto,
                "fecha_pago": p.fecha_pago.strftime("%d/%m/%Y"),
                "metodo": p.metodo.value if p.metodo else "—"
            }
            for p in pagos
        ]
    }


def reporte_ocupacion(db: Session):
    total = db.query(Habitacion).count()
    ocupadas = db.query(Habitacion).filter(
        Habitacion.estado == EstadoHabitacion.ocupada
    ).count()
    disponibles = db.query(Habitacion).filter(
        Habitacion.estado == EstadoHabitacion.disponible
    ).count()
    mantenimiento = db.query(Habitacion).filter(
        Habitacion.estado == EstadoHabitacion.mantenimiento
    ).count()

    return {
        "total_habitaciones": total,
        "ocupadas": ocupadas,
        "disponibles": disponibles,
        "en_mantenimiento": mantenimiento,
        "tasa_ocupacion": round((ocupadas / total * 100), 2) if total > 0 else 0,
        "tasa_disponibilidad": round((disponibles / total * 100), 2) if total > 0 else 0
    }


def reporte_deudores(db: Session):
    pagos_vencidos = db.query(Pago).filter(
        Pago.estado == EstadoPago.vencido
    ).all()

    deudores = {}
    for pago in pagos_vencidos:
        contrato = db.query(Contrato).filter(
            Contrato.id == pago.contrato_id
        ).first()
        if not contrato:
            continue
        inquilino = db.query(Inquilino).filter(
            Inquilino.id == contrato.inquilino_id
        ).first()
        if not inquilino:
            continue

        if inquilino.id not in deudores:
            deudores[inquilino.id] = {
                "inquilino_id": inquilino.id,
                "nombre": inquilino.nombre,
                "correo": inquilino.correo,
                "telefono": inquilino.telefono or "—",
                "total_deuda": 0,
                "pagos_vencidos": 0
            }
        deudores[inquilino.id]["total_deuda"] += pago.monto
        deudores[inquilino.id]["pagos_vencidos"] += 1

    resultado = list(deudores.values())
    for d in resultado:
        d["total_deuda"] = round(d["total_deuda"], 2)

    return {
        "total_deudores": len(resultado),
        "deuda_total_sistema": round(sum(d["total_deuda"] for d in resultado), 2),
        "detalle": resultado
    }


def reporte_resumen(db: Session):
    # Ingresos del mes actual
    ahora = datetime.utcnow()
    inicio_mes = ahora.replace(day=1, hour=0, minute=0, second=0)

    ingresos_mes = db.query(func.sum(Pago.monto)).filter(
        Pago.estado == EstadoPago.pagado,
        Pago.fecha_pago >= inicio_mes
    ).scalar() or 0

    # Pagos pendientes
    total_pendiente = db.query(func.sum(Pago.monto)).filter(
        Pago.estado == EstadoPago.pendiente
    ).scalar() or 0

    # Pagos vencidos
    total_vencido = db.query(func.sum(Pago.monto)).filter(
        Pago.estado == EstadoPago.vencido
    ).scalar() or 0

    # Contratos activos
    contratos_activos = db.query(Contrato).filter(
        Contrato.estado == EstadoContrato.activo
    ).count()

    # Ocupación
    ocupacion = reporte_ocupacion(db)

    return {
        "resumen_financiero": {
            "ingresos_mes_actual": round(ingresos_mes, 2),
            "total_pendiente_cobrar": round(total_pendiente, 2),
            "total_deuda_vencida": round(total_vencido, 2),
        },
        "resumen_contratos": {
            "contratos_activos": contratos_activos,
        },
        "resumen_habitaciones": {
            "total": ocupacion["total_habitaciones"],
            "ocupadas": ocupacion["ocupadas"],
            "disponibles": ocupacion["disponibles"],
            "tasa_ocupacion": ocupacion["tasa_ocupacion"]
        }
    }