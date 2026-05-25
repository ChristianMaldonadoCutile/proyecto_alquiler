from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from config.base_datos import SesionLocal
from modelos.pago import Pago, EstadoPago
from modelos.contrato import Contrato, EstadoContrato


def verificar_pagos_vencidos():
    db: Session = SesionLocal()
    try:
        ahora = datetime.utcnow()
        pagos = db.query(Pago).filter(
            Pago.estado == EstadoPago.pendiente,
            Pago.fecha_vencimiento < ahora
        ).all()
        for pago in pagos:
            pago.estado = EstadoPago.vencido
        db.commit()
        print(f"[{ahora.strftime('%d/%m/%Y %H:%M')}] Pagos vencidos actualizados: {len(pagos)}")
    finally:
        db.close()


def verificar_contratos_por_vencer():
    db: Session = SesionLocal()
    try:
        ahora = datetime.utcnow()
        limite = ahora + timedelta(days=30)
        contratos = db.query(Contrato).filter(
            Contrato.estado == EstadoContrato.activo,
            Contrato.fecha_fin <= limite
        ).all()
        for contrato in contratos:
            dias_restantes = (contrato.fecha_fin - ahora).days
            print(
                f"[ALERTA] Contrato #{contrato.id} vence en {dias_restantes} días "
                f"(Habitación: {contrato.habitacion_id} | Inquilino: {contrato.inquilino_id})"
            )
    finally:
        db.close()


def iniciar_scheduler():
    scheduler = BackgroundScheduler()

    # Verificar pagos vencidos cada hora
    scheduler.add_job(
        verificar_pagos_vencidos,
        "interval",
        hours=1,
        id="verificar_pagos",
        replace_existing=True
    )

    # Verificar contratos por vencer cada día a las 8am
    scheduler.add_job(
        verificar_contratos_por_vencer,
        "cron",
        hour=8,
        minute=0,
        id="verificar_contratos",
        replace_existing=True
    )

    scheduler.start()
    print("✅ Scheduler iniciado — verificando pagos y contratos automáticamente")
    return scheduler