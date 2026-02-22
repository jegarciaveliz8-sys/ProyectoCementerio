import os
import django
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch

# Configuración de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cementerio_config.settings')
django.setup()

from registros.models import Nicho

def generar_pdf_qr():
    nichos = Nicho.objects.filter(qr_code__isnull=False).order_by('codigo')
    c = canvas.Canvas("Planilla_QR_Sanarate.pdf", pagesize=letter)
    width, height = letter
    
    # Configuración de la cuadrícula
    cols = 4
    rows = 5
    margin = 0.5 * inch
    box_width = (width - 2*margin) / cols
    box_height = (height - 2*margin) / rows
    
    x, y = margin, height - margin - box_height
    count = 0

    print(f"📄 Generando PDF para {nichos.count()} nichos...")

    for n in nichos:
        # Dibujar el QR (ajustando la ruta para Cloudinary o Local)
        try:
            # Si usas Cloudinary, necesitamos la ruta local o descargarla, 
            # pero como los generamos en MEDIA_ROOT:
            qr_path = n.qr_code.path
            c.drawImage(qr_path, x + 0.2*inch, y + 0.4*inch, width=1.2*inch, height=1.2*inch)
            
            # Dibujar el texto del código
            c.setFont("Helvetica-Bold", 10)
            c.drawCentredString(x + box_width/2, y + 0.2*inch, f"NICHO: {n.codigo}")
            c.setFont("Helvetica", 7)
            c.drawCentredString(x + box_width/2, y + 0.05*inch, "Muni Sanarate")
        except Exception as e:
            print(f"Error en {n.codigo}: {e}")

        # Mover a la siguiente posición
        count += 1
        x += box_width
        if count % cols == 0:
            x = margin
            y -= box_height
        
        if count % (cols * rows) == 0:
            c.showPage()
            x, y = margin, height - margin - box_height

    c.save()
    print("✅ ¡PDF 'Planilla_QR_Sanarate.pdf' creado con éxito!")

if __name__ == "__main__":
    generar_pdf_qr()
