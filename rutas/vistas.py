import os
from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional

from config.base_datos import obtener_db
from modelos.habitacion import EstadoHabitacion
from modelos.pago import EstadoPago
from modelos.contrato import Contrato
from modelos.inquilino import Inquilino
from modelos.habitacion import Habitacion
from servicios.servicio_recibo import generar_recibo
import controladores.controlador_propietario as ctrl_propietario
import controladores.controlador_inquilino as ctrl_inquilino
import controladores.controlador_habitacion as ctrl_habitacion
import controladores.controlador_contrato as ctrl_contrato
import controladores.controlador_pago as ctrl_pago
import controladores.controlador_reporte as ctrl_reporte

enrutador = APIRouter(prefix="/vistas")
templates = Jinja2Templates(directory=os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates"))


def tr(request: Request, name: str, context: dict = {}):
    return templates.TemplateResponse(request=request, name=name, context=context)


def obtener_token_cookie(request: Request):
    return request.cookies.get("access_token")


def verificar_sesion(request: Request, db: Session):
    token = obtener_token_cookie(request)
    if not token:
        return None
    try:
        return ctrl_propietario.obtener_propietario_actual(db, token)
    except:
        return None


# ─── LOGIN ───────────────────────────────────────────────────────────────────

@enrutador.get("/login", response_class=HTMLResponse)
async def vista_login(request: Request):
    return tr(request, "login.html")


@enrutador.post("/login")
async def procesar_login(
    request: Request,
    correo: str = Form(...),
    contrasena: str = Form(...),
    db: Session = Depends(obtener_db)
):
    # Intentar login como propietario
    try:
        resultado = ctrl_propietario.autenticar(db, correo, contrasena)
        respuesta = RedirectResponse(url="/vistas/inicio", status_code=302)
        respuesta.set_cookie(key="access_token", value=resultado["access_token"], httponly=True)
        return respuesta
    except:
        pass

    # Intentar login como inquilino
    try:
        resultado = ctrl_inquilino.autenticar(db, correo, contrasena)
        respuesta = RedirectResponse(url="/inquilino/portal", status_code=302)
        respuesta.set_cookie(key="token_inquilino", value=resultado["access_token"], httponly=True)
        return respuesta
    except:
        pass

    # Si ninguno funcionó
    return tr(request, "login.html", {
        "mensaje_error": "Correo o contraseña incorrectos"
    })


@enrutador.get("/logout")
async def logout():
    respuesta = RedirectResponse(url="/vistas/login", status_code=302)
    respuesta.delete_cookie("access_token")
    respuesta.delete_cookie("token_inquilino")
    return respuesta


# ─── INICIO ──────────────────────────────────────────────────────────────────

@enrutador.get("/inicio", response_class=HTMLResponse)
async def vista_inicio(request: Request, db: Session = Depends(obtener_db)):
    propietario = verificar_sesion(request, db)
    if not propietario:
        return RedirectResponse(url="/vistas/login", status_code=302)
    resumen = ctrl_reporte.reporte_resumen(db)
    return tr(request, "inicio.html", {"propietario": propietario, "resumen": resumen})


# ─── HABITACIONES ────────────────────────────────────────────────────────────

@enrutador.get("/habitaciones", response_class=HTMLResponse)
async def vista_habitaciones(
    request: Request,
    estado: Optional[str] = None,
    db: Session = Depends(obtener_db)
):
    propietario = verificar_sesion(request, db)
    if not propietario:
        return RedirectResponse(url="/vistas/login", status_code=302)
    habitaciones = ctrl_habitacion.obtener_todas(db)
    if estado:
        habitaciones = [h for h in habitaciones if h.estado == estado]
    return tr(request, "habitaciones.html", {"habitaciones": habitaciones, "estado_filtro": estado})


@enrutador.get("/habitaciones/crear", response_class=HTMLResponse)
async def vista_crear_habitacion(request: Request, db: Session = Depends(obtener_db)):
    propietario = verificar_sesion(request, db)
    if not propietario:
        return RedirectResponse(url="/vistas/login", status_code=302)
    return tr(request, "form_habitacion.html")


@enrutador.post("/habitaciones/crear")
async def procesar_crear_habitacion(
    request: Request,
    numero: str = Form(...),
    piso: Optional[int] = Form(None),
    descripcion: Optional[str] = Form(None),
    precio_mensual: float = Form(...),
    db: Session = Depends(obtener_db)
):
    propietario = verificar_sesion(request, db)
    if not propietario:
        return RedirectResponse(url="/vistas/login", status_code=302)
    try:
        from esquemas.habitacion import HabitacionCrear
        datos = HabitacionCrear(
            numero=numero,
            piso=piso,
            descripcion=descripcion,
            precio_mensual=precio_mensual,
            propietario_id=propietario.id
        )
        ctrl_habitacion.crear(db, datos)
        return RedirectResponse(url="/vistas/habitaciones", status_code=302)
    except Exception as e:
        return tr(request, "form_habitacion.html", {"mensaje_error": str(e)})


@enrutador.get("/habitaciones/{habitacion_id}/editar", response_class=HTMLResponse)
async def vista_editar_habitacion(
    request: Request,
    habitacion_id: int,
    db: Session = Depends(obtener_db)
):
    propietario = verificar_sesion(request, db)
    if not propietario:
        return RedirectResponse(url="/vistas/login", status_code=302)
    habitacion = ctrl_habitacion.obtener_por_id(db, habitacion_id)
    return tr(request, "form_habitacion.html", {"habitacion": habitacion})


@enrutador.post("/habitaciones/{habitacion_id}/editar")
async def procesar_editar_habitacion(
    request: Request,
    habitacion_id: int,
    numero: str = Form(...),
    piso: Optional[int] = Form(None),
    descripcion: Optional[str] = Form(None),
    precio_mensual: float = Form(...),
    estado: str = Form(...),
    db: Session = Depends(obtener_db)
):
    propietario = verificar_sesion(request, db)
    if not propietario:
        return RedirectResponse(url="/vistas/login", status_code=302)
    from esquemas.habitacion import HabitacionActualizar
    datos = HabitacionActualizar(
        numero=numero, piso=piso, descripcion=descripcion,
        precio_mensual=precio_mensual, estado=estado
    )
    ctrl_habitacion.actualizar(db, habitacion_id, datos)
    return RedirectResponse(url="/vistas/habitaciones", status_code=302)


@enrutador.get("/habitaciones/{habitacion_id}/eliminar")
async def eliminar_habitacion(
    request: Request, habitacion_id: int, db: Session = Depends(obtener_db)
):
    propietario = verificar_sesion(request, db)
    if not propietario:
        return RedirectResponse(url="/vistas/login", status_code=302)
    ctrl_habitacion.eliminar(db, habitacion_id)
    return RedirectResponse(url="/vistas/habitaciones", status_code=302)


# ─── INQUILINOS ──────────────────────────────────────────────────────────────

@enrutador.get("/inquilinos", response_class=HTMLResponse)
async def vista_inquilinos(request: Request, db: Session = Depends(obtener_db)):
    propietario = verificar_sesion(request, db)
    if not propietario:
        return RedirectResponse(url="/vistas/login", status_code=302)
    inquilinos = ctrl_inquilino.obtener_todos(db)
    return tr(request, "inquilinos.html", {"inquilinos": inquilinos})


@enrutador.get("/inquilinos/crear", response_class=HTMLResponse)
async def vista_crear_inquilino(request: Request, db: Session = Depends(obtener_db)):
    propietario = verificar_sesion(request, db)
    if not propietario:
        return RedirectResponse(url="/vistas/login", status_code=302)
    return tr(request, "form_inquilino.html")


@enrutador.post("/inquilinos/crear")
async def procesar_crear_inquilino(
    request: Request,
    nombre: str = Form(...),
    dni: str = Form(...),
    correo: str = Form(...),
    telefono: Optional[str] = Form(None),
    contacto_emergencia: Optional[str] = Form(None),
    telefono_emergencia: Optional[str] = Form(None),
    contrasena: str = Form(...),
    db: Session = Depends(obtener_db)
):
    propietario = verificar_sesion(request, db)
    if not propietario:
        return RedirectResponse(url="/vistas/login", status_code=302)
    try:
        from esquemas.inquilino import InquilinoCrear
        datos = InquilinoCrear(
            nombre=nombre, dni=dni, correo=correo, telefono=telefono,
            contacto_emergencia=contacto_emergencia,
            telefono_emergencia=telefono_emergencia,
            contrasena=contrasena
        )
        ctrl_inquilino.crear(db, datos)
        return RedirectResponse(url="/vistas/inquilinos", status_code=302)
    except Exception as e:
        return tr(request, "form_inquilino.html", {"mensaje_error": str(e)})


@enrutador.get("/inquilinos/{inquilino_id}/editar", response_class=HTMLResponse)
async def vista_editar_inquilino(
    request: Request, inquilino_id: int, db: Session = Depends(obtener_db)
):
    propietario = verificar_sesion(request, db)
    if not propietario:
        return RedirectResponse(url="/vistas/login", status_code=302)
    inquilino = ctrl_inquilino.obtener_por_id(db, inquilino_id)
    return tr(request, "form_inquilino.html", {"inquilino": inquilino})


@enrutador.post("/inquilinos/{inquilino_id}/editar")
async def procesar_editar_inquilino(
    request: Request,
    inquilino_id: int,
    nombre: str = Form(...),
    correo: str = Form(...),
    telefono: Optional[str] = Form(None),
    contacto_emergencia: Optional[str] = Form(None),
    telefono_emergencia: Optional[str] = Form(None),
    contrasena: Optional[str] = Form(None),
    db: Session = Depends(obtener_db)
):
    propietario = verificar_sesion(request, db)
    if not propietario:
        return RedirectResponse(url="/vistas/login", status_code=302)
    from esquemas.inquilino import InquilinoActualizar
    datos = InquilinoActualizar(
        nombre=nombre, correo=correo, telefono=telefono,
        contacto_emergencia=contacto_emergencia,
        telefono_emergencia=telefono_emergencia,
        contrasena=contrasena if contrasena else None
    )
    ctrl_inquilino.actualizar(db, inquilino_id, datos)
    return RedirectResponse(url="/vistas/inquilinos", status_code=302)


@enrutador.get("/inquilinos/{inquilino_id}/eliminar")
async def eliminar_inquilino(
    request: Request, inquilino_id: int, db: Session = Depends(obtener_db)
):
    propietario = verificar_sesion(request, db)
    if not propietario:
        return RedirectResponse(url="/vistas/login", status_code=302)
    ctrl_inquilino.eliminar(db, inquilino_id)
    return RedirectResponse(url="/vistas/inquilinos", status_code=302)


# ─── CONTRATOS ───────────────────────────────────────────────────────────────

@enrutador.get("/contratos", response_class=HTMLResponse)
async def vista_contratos(request: Request, db: Session = Depends(obtener_db)):
    propietario = verificar_sesion(request, db)
    if not propietario:
        return RedirectResponse(url="/vistas/login", status_code=302)
    contratos = ctrl_contrato.obtener_todos(db)
    return tr(request, "contratos.html", {"contratos": contratos})


@enrutador.get("/contratos/crear", response_class=HTMLResponse)
async def vista_crear_contrato(request: Request, db: Session = Depends(obtener_db)):
    propietario = verificar_sesion(request, db)
    if not propietario:
        return RedirectResponse(url="/vistas/login", status_code=302)
    habitaciones = ctrl_habitacion.obtener_disponibles(db)
    inquilinos = ctrl_inquilino.obtener_todos(db)
    return tr(request, "form_contrato.html", {"habitaciones": habitaciones, "inquilinos": inquilinos})


@enrutador.post("/contratos/crear")
async def procesar_crear_contrato(
    request: Request,
    habitacion_id: int = Form(...),
    inquilino_id: int = Form(...),
    fecha_inicio: str = Form(...),
    fecha_fin: str = Form(...),
    monto_mensual: float = Form(...),
    dia_vencimiento: int = Form(...),
    db: Session = Depends(obtener_db)
):
    propietario = verificar_sesion(request, db)
    if not propietario:
        return RedirectResponse(url="/vistas/login", status_code=302)
    try:
        from esquemas.contrato import ContratoCrear
        datos = ContratoCrear(
            habitacion_id=habitacion_id,
            inquilino_id=inquilino_id,
            fecha_inicio=datetime.fromisoformat(fecha_inicio),
            fecha_fin=datetime.fromisoformat(fecha_fin),
            monto_mensual=monto_mensual,
            dia_vencimiento=dia_vencimiento
        )
        ctrl_contrato.crear(db, datos)
        return RedirectResponse(url="/vistas/contratos", status_code=302)
    except Exception as e:
        habitaciones = ctrl_habitacion.obtener_disponibles(db)
        inquilinos = ctrl_inquilino.obtener_todos(db)
        return tr(request, "form_contrato.html", {
            "habitaciones": habitaciones,
            "inquilinos": inquilinos,
            "mensaje_error": str(e)
        })


@enrutador.get("/contratos/{contrato_id}/finalizar")
async def finalizar_contrato(
    request: Request, contrato_id: int, db: Session = Depends(obtener_db)
):
    propietario = verificar_sesion(request, db)
    if not propietario:
        return RedirectResponse(url="/vistas/login", status_code=302)
    ctrl_contrato.finalizar(db, contrato_id)
    return RedirectResponse(url="/vistas/contratos", status_code=302)


# ─── PAGOS ───────────────────────────────────────────────────────────────────

@enrutador.get("/pagos", response_class=HTMLResponse)
async def vista_pagos(
    request: Request,
    estado: Optional[str] = None,
    db: Session = Depends(obtener_db)
):
    propietario = verificar_sesion(request, db)
    if not propietario:
        return RedirectResponse(url="/vistas/login", status_code=302)
    pagos = ctrl_pago.obtener_todos(db)
    if estado:
        pagos = [p for p in pagos if p.estado == estado]
    return tr(request, "pagos.html", {"pagos": pagos, "estado_filtro": estado})


@enrutador.get("/pagos/{pago_id}/registrar", response_class=HTMLResponse)
async def vista_registrar_pago(
    request: Request, pago_id: int, db: Session = Depends(obtener_db)
):
    propietario = verificar_sesion(request, db)
    if not propietario:
        return RedirectResponse(url="/vistas/login", status_code=302)
    pago = ctrl_pago.obtener_por_id(db, pago_id)
    return tr(request, "form_pago.html", {"pago": pago})


@enrutador.post("/pagos/{pago_id}/registrar")
async def procesar_registrar_pago(
    request: Request,
    pago_id: int,
    metodo: str = Form(...),
    observacion: Optional[str] = Form(None),
    db: Session = Depends(obtener_db)
):
    propietario = verificar_sesion(request, db)
    if not propietario:
        return RedirectResponse(url="/vistas/login", status_code=302)
    from esquemas.pago import PagoRegistrar
    datos = PagoRegistrar(metodo=metodo, observacion=observacion)
    ctrl_pago.registrar_pago(db, pago_id, datos)
    return RedirectResponse(url="/vistas/pagos", status_code=302)


@enrutador.get("/pagos/{pago_id}/recibo")
async def descargar_recibo_vista(
    request: Request, pago_id: int, db: Session = Depends(obtener_db)
):
    propietario = verificar_sesion(request, db)
    if not propietario:
        return RedirectResponse(url="/vistas/login", status_code=302)
    pago = ctrl_pago.obtener_por_id(db, pago_id)
    contrato = db.query(Contrato).filter(Contrato.id == pago.contrato_id).first()
    inquilino = db.query(Inquilino).filter(Inquilino.id == contrato.inquilino_id).first()
    habitacion = db.query(Habitacion).filter(Habitacion.id == contrato.habitacion_id).first()
    pdf = generar_recibo(pago, contrato, inquilino, habitacion)
    return Response(
        content=pdf,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=recibo_pago_{pago_id:04d}.pdf"}
    )


# ─── REPORTES ────────────────────────────────────────────────────────────────

@enrutador.get("/reportes", response_class=HTMLResponse)
async def vista_reportes(
    request: Request,
    fecha_inicio: Optional[str] = None,
    fecha_fin: Optional[str] = None,
    db: Session = Depends(obtener_db)
):
    propietario = verificar_sesion(request, db)
    if not propietario:
        return RedirectResponse(url="/vistas/login", status_code=302)
    resumen = ctrl_reporte.reporte_resumen(db)
    ocupacion = ctrl_reporte.reporte_ocupacion(db)
    deudores = ctrl_reporte.reporte_deudores(db)
    ingresos = None
    if fecha_inicio and fecha_fin:
        ingresos = ctrl_reporte.reporte_ingresos(
            db,
            datetime.fromisoformat(fecha_inicio),
            datetime.fromisoformat(fecha_fin)
        )
    return tr(request, "reportes.html", {
        "resumen": resumen,
        "ocupacion": ocupacion,
        "deudores": deudores,
        "ingresos": ingresos,
        "fecha_inicio": fecha_inicio,
        "fecha_fin": fecha_fin
    })