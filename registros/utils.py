from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.units import inch
from django.http import HttpResponse
import io

def generar_pdf_titulo(registro):
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=LETTER)
    
    # Borde de Seguridad
    p.setLineWidth(3)
    p.rect(0.5*inch, 0.5*inch, 7.5*inch, 10*inch)
    
    # Encabezado
    p.setFont("Helvetica-Bold", 18)
    p.drawCentredString(4.25*inch, 9.5*inch, "MUNICIPALIDAD DE SANARATE")
    p.setFont("Helvetica", 12)
    p.drawCentredString(4.25*inch, 9.2*inch, "Departamento de Cementerios")
    
    # Título
    p.setFont("Helvetica-Bold", 16)
    p.drawCentredString(4.25*inch, 8.5*inch, "TÍTULO DE DERECHO DE ARRENDAMIENTO")
    
    # Contenido
    p.setFont("Helvetica", 12)
    texto = [
        f"Por medio de la presente, se hace constar que el nicho código: {registro.nicho.codigo}",
        f"ubicado en: {registro.nicho.edificio.nombre}",
        f"ha sido asignado para el descanso eterno de:",
        "",
        f"DIFUNTO: {registro.nombre_completo.upper()}",
        "",
        f"Fecha de inhumación: {registro.fecha_fallecimiento}",
        f"Estado del contrato: VIGENTE / AL DÍA",
    ]
    
    y = 7.5*inch
    for linea in texto:
        p.drawString(1*inch, y, linea)
        y -= 0.3*inch
        
    # Sello Digital (QR Simulado)
    p.rect(6*inch, 1*inch, 1.5*inch, 1.5*inch)
    p.setFont("Helvetica-Oblique", 8)
    p.drawString(6*inch, 0.8*inch, "SELLO DIGITAL DE VALIDEZ")
    
    p.showPage()
    p.save()
    buffer.seek(0)
    return buffer
