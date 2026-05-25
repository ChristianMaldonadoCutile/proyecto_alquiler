from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from io import BytesIO
from datetime import datetime

from modelos.pago import Pago
from modelos.contrato import Contrato
from modelos.inquilino import Inquilino
from modelos.habitacion import Habitacion


def generar_recibo(pago: Pago, contrato: Contrato, inquilino: Inquilino, habitacion: Habitacion) -> bytes:
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=inch,
        leftMargin=inch,
        topMargin=inch,
        bottomMargin=inch
    )

    estilos = getSampleStyleSheet()
    elementos = []

    # Estilo título
    estilo_titulo = ParagraphStyle(
        "titulo",
        parent=estilos["Heading1"],
        fontSize=20,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#2C3E50"),
        spaceAfter=10
    )

    # Estilo subtítulo
    estilo_subtitulo = ParagraphStyle(
        "subtitulo",
        parent=estilos["Normal"],
        fontSize=11,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#7F8C8D"),
        spaceAfter=20
    )

    # Estilo derecha
    estilo_derecha = ParagraphStyle(
        "derecha",
        parent=estilos["Normal"],
        fontSize=10,
        alignment=TA_RIGHT,
        textColor=colors.HexColor("#7F8C8D")
    )

    # Título
    elementos.append(Paragraph("RECIBO DE ALQUILER", estilo_titulo))
    elementos.append(Paragraph("Sistema de Cobros de Alquiler", estilo_subtitulo))
    elementos.append(Paragraph(
        f"Fecha de emisión: {datetime.now().strftime('%d/%m/%Y %H:%M')}",
        estilo_derecha
    ))
    elementos.append(Spacer(1, 20))

    # Datos del recibo
    datos_recibo = [
        ["RECIBO N°", f"#{pago.id:04d}"],
        ["Estado", pago.estado.value.upper()],
        ["Método de pago", pago.metodo.value.capitalize() if pago.metodo else "—"],
        ["Fecha de pago", pago.fecha_pago.strftime("%d/%m/%Y") if pago.fecha_pago else "—"],
        ["Fecha de vencimiento", pago.fecha_vencimiento.strftime("%d/%m/%Y")],
    ]

    tabla_recibo = Table(datos_recibo, colWidths=[2.5 * inch, 4 * inch])
    tabla_recibo.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#2C3E50")),
        ("TEXTCOLOR", (0, 0), (0, -1), colors.white),
        ("BACKGROUND", (1, 0), (1, -1), colors.HexColor("#ECF0F1")),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("PADDING", (0, 0), (-1, -1), 8),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#BDC3C7")),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
    ]))
    elementos.append(tabla_recibo)
    elementos.append(Spacer(1, 20))

    # Datos del inquilino
    elementos.append(Paragraph("DATOS DEL INQUILINO", ParagraphStyle(
        "seccion", parent=estilos["Heading2"],
        fontSize=13, textColor=colors.HexColor("#2C3E50"), spaceAfter=8
    )))

    datos_inquilino = [
        ["Nombre", inquilino.nombre],
        ["DNI", inquilino.dni],
        ["Correo", inquilino.correo],
        ["Teléfono", inquilino.telefono or "—"],
    ]

    tabla_inquilino = Table(datos_inquilino, colWidths=[2.5 * inch, 4 * inch])
    tabla_inquilino.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#3498DB")),
        ("TEXTCOLOR", (0, 0), (0, -1), colors.white),
        ("BACKGROUND", (1, 0), (1, -1), colors.HexColor("#EBF5FB")),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("PADDING", (0, 0), (-1, -1), 8),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#BDC3C7")),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
    ]))
    elementos.append(tabla_inquilino)
    elementos.append(Spacer(1, 20))

    # Datos de la habitación
    elementos.append(Paragraph("DATOS DE LA HABITACIÓN", ParagraphStyle(
        "seccion2", parent=estilos["Heading2"],
        fontSize=13, textColor=colors.HexColor("#2C3E50"), spaceAfter=8
    )))

    datos_habitacion = [
        ["Número", habitacion.numero],
        ["Piso", str(habitacion.piso) if habitacion.piso else "—"],
        ["Descripción", habitacion.descripcion or "—"],
        ["Precio mensual", f"Bs. {habitacion.precio_mensual:.2f}"],
    ]

    tabla_habitacion = Table(datos_habitacion, colWidths=[2.5 * inch, 4 * inch])
    tabla_habitacion.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#27AE60")),
        ("TEXTCOLOR", (0, 0), (0, -1), colors.white),
        ("BACKGROUND", (1, 0), (1, -1), colors.HexColor("#EAFAF1")),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("PADDING", (0, 0), (-1, -1), 8),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#BDC3C7")),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
    ]))
    elementos.append(tabla_habitacion)
    elementos.append(Spacer(1, 20))

    # Total
    datos_total = [
        ["MONTO PAGADO", f"Bs. {pago.monto:.2f}"],
    ]
    tabla_total = Table(datos_total, colWidths=[2.5 * inch, 4 * inch])
    tabla_total.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#2C3E50")),
        ("TEXTCOLOR", (0, 0), (-1, -1), colors.white),
        ("FONTSIZE", (0, 0), (-1, -1), 14),
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica-Bold"),
        ("PADDING", (0, 0), (-1, -1), 12),
        ("ALIGN", (1, 0), (1, 0), "RIGHT"),
    ]))
    elementos.append(tabla_total)
    elementos.append(Spacer(1, 30))

    # Observación
    if pago.observacion:
        elementos.append(Paragraph(f"Observación: {pago.observacion}", estilos["Normal"]))
        elementos.append(Spacer(1, 20))

    # Pie de página
    elementos.append(Paragraph(
        "Este recibo es un comprobante válido de pago.",
        ParagraphStyle("pie", parent=estilos["Normal"],
                       fontSize=9, alignment=TA_CENTER,
                       textColor=colors.HexColor("#7F8C8D"))
    ))

    doc.build(elementos)
    buffer.seek(0)
    return buffer.getvalue()