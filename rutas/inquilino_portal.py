import os
from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import Optional

from config.base_datos import obtener_db
from modelos.contrato import Contrato
from modelos.pago import Pago, EstadoPago
from modelos.habitacion import Habitacion
from servicios.servicio_recibo import generar_recibo
import controladores.controlador_inquilino as ctrl_inquilino

enrutador = APIRouter(prefix="/inquilino")
templates = Jinja2Templates(directory=os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates"))


def tr(request: Request, name: str, context: dict = {}):
    return templates.TemplateResponse(request=request, name=name, context=context)


def obtener_token_cookie(request: Request):
    return request.cookies.get("token_inquilino")


def verificar_sesion(request: Request, db: Session):
    token = obtener_token_cookie(request)
    if not token:
        return None
    try:
        return ctrl_inquilino.obtener_inquilino_actual(db, token)
    except:
        return None


# ─── LOGIN ───────────────────────────────────────────────────────────────────

@enrutador.get("/login", response_class=HTMLResponse)
async def vista_login(request: Request):
    return tr(request, "login_inquilino.html")


@enrutador.post("/login")
async def procesar_login(
    request: Request,
    correo: str = Form(...),
    contrasena: str = Form(...),
    db: Session = Depends(obtener_db)
):
    try:
        resultado = ctrl_inquilino.autenticar(db, correo, contrasena)
        respuesta = RedirectResponse(url="/inquilino/portal", status_code=302)
        respuesta.set_cookie(key="token_inquilino", value=resultado["access_token"], httponly=True)
        return respuesta
    except:
        return tr(request, "login_inquilino.html", {
            "mensaje_error": "Correo o contraseña incorrectos"
        })


@enrutador.get("/logout")
async def logout():
    respuesta = RedirectResponse(url="/inquilino/login", status_code=302)
    respuesta.delete_cookie("token_inquilino")
    return respuesta


# ─── PORTAL ──────────────────────────────────────────────────────────────────

@enrutador.get("/portal", response_class=HTMLResponse)
async def portal(request: Request, db: Session = Depends(obtener_db)):
    inquilino = verificar_sesion(request, db)
    if not inquilino:
        return RedirectResponse(url="/inquilino/login", status_code=302)

    # Obtener contratos del inquilino
    contratos = db.query(Contrato).filter(
        Contrato.inquilino_id == inquilino.id
    ).all()

    # Obtener todos los pagos del inquilino
    todos_pagos = []
    for contrato in contratos:
        pagos = db.query(Pago).filter(
            Pago.contrato_id == contrato.id
        ).order_by(Pago.fecha_vencimiento).all()
        todos_pagos.extend(pagos)

    pendientes = [p for p in todos_pagos if p.estado == EstadoPago.pendiente]
    vencidos = [p for p in todos_pagos if p.estado == EstadoPago.vencido]
    pagados = [p for p in todos_pagos if p.estado == EstadoPago.pagado]

    return tr(request, "portal_inquilino.html", {
        "inquilino": inquilino,
        "todos_pagos": todos_pagos,
        "pendientes": pendientes,
        "vencidos": vencidos,
        "pagados": pagados
    })


# ─── RECIBO ──────────────────────────────────────────────────────────────────

@enrutador.get("/pagos/{pago_id}/recibo")
async def descargar_recibo(
    request: Request,
    pago_id: int,
    db: Session = Depends(obtener_db)
):
    inquilino = verificar_sesion(request, db)
    if not inquilino:
        return RedirectResponse(url="/inquilino/login", status_code=302)

    pago = db.query(Pago).filter(Pago.id == pago_id).first()
    if not pago:
        return RedirectResponse(url="/inquilino/portal", status_code=302)

    # Verificar que el pago pertenece al inquilino
    contrato = db.query(Contrato).filter(Contrato.id == pago.contrato_id).first()
    if not contrato or contrato.inquilino_id != inquilino.id:
        return RedirectResponse(url="/inquilino/portal", status_code=302)

    habitacion = db.query(Habitacion).filter(Habitacion.id == contrato.habitacion_id).first()
    pdf = generar_recibo(pago, contrato, inquilino, habitacion)

    return Response(
        content=pdf,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=recibo_pago_{pago_id:04d}.pdf"}
    )