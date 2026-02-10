from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.units import inch
from reportlab.lib import colors
import io
import uuid

def generar_titulo_pdf(registro):
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=LETTER)
    width, height = LETTER

    # --- 1. SELLO DE AGUA SEGURIDAD ---
    p.saveState()
    p.setFont('Helvetica-Bold', 60)
    p.setStrokeColor(colors.lightgrey)
    p.setFillColor(colors.lightgrey)
    p.setFillAlpha(0.2)
    p.translate(width/2, height/2)
    p.rotate(45)
    p.drawCentredString(0, 0, "MUNICIPALIDAD DE SANARATE")
    p.restoreState()

    # --- 2. ENCABEZADO INDUSTRIAL ---
    p.setFont("Helvetica-Bold", 16)
    p.drawCentredString(width/2, height - 1*inch, "ESTADO DE GUATEMALA")
    p.setFont("Helvetica-Bold", 14)
    p.drawCentredString(width/2, height - 1.3*inch, "MUNICIPALIDAD DE SANARATE, EL PROGRESO")
    p.setFont("Helvetica", 10)
    p.drawCentredString(width/2, height - 1.5*inch, "Departamento de Servicios Públicos - Cementerio Municipal")

    # --- 3. CUERPO DEL TÍTULO ---
    p.line(1*inch, height - 1.8*inch, width - 1*inch, height - 1.8*inch)
    p.setFont("Helvetica-Bold", 18)
    p.drawCentredString(width/2, height - 2.5*inch, "TÍTULO DE PERPETUIDAD")

    text_body = [
        f"Por medio de la presente, la Municipalidad de Sanarate hace constar que:",
        f"El/La señor(a) {registro.responsable.upper()} es poseedor(a) del espacio",
        f"identificado como: {registro.espacio.codigo_ubicacion} en el {registro.espacio.sector.nombre}.",
        f"",
        f"Datos del Inhumado: {registro.nombre_completo.upper()}",
        f"Fecha de Inhumación: {registro.fecha_inhumacion}",
        f"Estado de Solvencia: SOLVENTE HASTA {registro.ultimo_pago_anual}"
    ]

    y = height - 3.5*inch
    p.setFont("Helvetica", 12)
    for line in text_body:
        p.drawString(1.5*inch, y, line)
        y -= 0.3*inch

    # --- 4. FIRMA Y VALIDACIÓN ---
    p.line(width/2 - 1*inch, 2.5*inch, width/2 + 1*inch, 2.5*inch)
    p.setFont("Helvetica-Bold", 10)
    p.drawCentredString(width/2, 2.3*inch, "ADMINISTRADOR DE CEMENTERIO")
    
    # Código único de verificación (UUID)
    codigo_verificacion = str(uuid.uuid4())[:8].upper()
    p.setFont("Courier-Bold", 9)
    p.drawRightString(width - 1*inch, 1*inch, f"CÓDIGO DE VERIFICACIÓN: {codigo_verificacion}")
    p.drawString(1*inch, 1*inch, f"FECHA DE EMISIÓN: {registro.fecha_inhumacion}")

    p.showPage()
    p.save()
    buffer.seek(0)
    return buffer
