from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponse
from django.db.models import Sum, Q
from django.utils import timezone
from django.conf import settings
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from .models import Nicho, ReporteDano
import io
import os
import hashlib

# --- UTILIDAD: DIBUJAR MARCO Y MEMBRETE PRO ---
def aplicar_estilo_seguridad(p, width, height, titulo, color_principal=colors.black):
    logo_path = os.path.join(settings.BASE_DIR, 'registros', 'static', 'img', 'logo_muni.png')
    
    # 1. Marco Ornamental
    p.setStrokeColor(color_principal)
    p.setLineWidth(2)
    p.rect(40, 40, width-80, height-80)
    p.setLineWidth(0.5)
    p.rect(45, 45, width-90, height-90)

    # 2. Marca de Agua
    if os.path.exists(logo_path):
        p.saveState()
        p.setFillAlpha(0.04)
        p.drawImage(logo_path, width/2-150, height/2-150, width=300, height=300, mask='auto')
        p.restoreState()

    # 3. Encabezado
    if os.path.exists(logo_path):
        p.drawImage(logo_path, 60, 705, width=65, height=65, mask='auto')
    
    p.setFont("Helvetica-Bold", 16)
    p.drawCentredString(width/2 + 30, 740, "MUNICIPALIDAD DE SANARATE, EL PROGRESO")
    p.setFont("Helvetica", 10)
    p.drawCentredString(width/2 + 30, 725, "ADMINISTRACIÓN INTEGRAL DE CEMENTERIOS")
    p.setStrokeColor(colors.black)
    p.line(60, 700, width-60, 700)
    
    p.setFillColor(color_principal)
    p.setFont("Helvetica-Bold", 20)
    p.drawCentredString(width/2, 650, titulo)
    p.setFillColor(colors.black)

# --- VISTAS DE DASHBOARD Y MAPA ---
def dashboard(request):
    total = Nicho.objects.count()
    ocupados = Nicho.objects.exclude(Q(nombre_difunto__isnull=True) | Q(nombre_difunto="")).count()
    disponibles = total - ocupados
    mora_count = Nicho.objects.filter(monto_arbitrio__lte=0).exclude(nombre_difunto="").count()
    recaudado = Nicho.objects.aggregate(Sum('monto_arbitrio'))['monto_arbitrio__sum'] or 0
    return render(request, 'registros/dashboard.html', {
        'total': total, 'ocupados': ocupados, 'disponibles': disponibles, 
        'mora_total': mora_count, 'recaudado': recaudado
    })

def mapa_cimenterio(request):
    nichos = Nicho.objects.exclude(lat__isnull=True).exclude(lng__isnull=True)
    return render(request, 'registros/mapa.html', {'nichos': nichos})

def datos_nichos_json(request):
    query = request.GET.get('q', '')
    nichos = Nicho.objects.filter(Q(codigo__icontains=query) | Q(nombre_difunto__icontains=query)) if query else Nicho.objects.all()
    data = [{'id': n.id, 'codigo': n.codigo, 'nombre_difunto': n.nombre_difunto or 'DISPONIBLE', 'lat': n.lat, 'lng': n.lng} for n in nichos]
    return JsonResponse(data, safe=False)

# --- DOCUMENTOS NIVEL MUNDIAL ---

def generar_titulo_propiedad(request, nicho_id):
    obj = get_object_or_404(Nicho, id=nicho_id)
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    
    aplicar_estilo_seguridad(p, width, height, "TÍTULO DE PROPIEDAD PERPETUA", colors.black)
    
    p.setFont("Helvetica", 12)
    p.drawCentredString(width/2, 580, "POR TANTO, SE RECONOCE EL DERECHO DE PROPIEDAD A:")
    p.setFont("Helvetica-Bold", 16)
    p.drawCentredString(width/2, 550, f"{obj.propietario or 'SIN REGISTRO'}")
    
    p.setFont("Helvetica", 12)
    p.drawCentredString(width/2, 510, f"Correspondiente al Nicho Código: {obj.codigo}")
    
    # Datos GPS
    p.setFont("Courier-Bold", 10)
    p.drawCentredString(width/2, 450, f"COORDENADAS GIS: {obj.lat}, {obj.lng}")
    
    # QR y Hash
    h = hashlib.sha256(f"TIT-{obj.id}-{obj.codigo}".encode()).hexdigest()[:16].upper()
    if obj.qr_code: p.drawImage(obj.qr_code.path, 460, 60, width=80, height=80)
    p.setFont("Courier", 8); p.setFillAlpha(0.5)
    p.drawString(60, 55, f"VERIFICACIÓN_TITULO: {h}"); p.setFillAlpha(1)
    
    p.showPage(); p.save(); buffer.seek(0)
    return HttpResponse(buffer, content_type='application/pdf')

def pdf_solvencia_municipal(request, nicho_id):
    obj = get_object_or_404(Nicho, id=nicho_id)
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    
    aplicar_estilo_seguridad(p, width, height, "CERTIFICADO DE SOLVENCIA", colors.dodgerblue)
    
    p.setFont("Helvetica", 12)
    p.drawCentredString(width/2, 550, f"Se certifica que el contribuyente: {obj.propietario or 'S/P'}")
    p.drawCentredString(width/2, 530, f"responsable del nicho {obj.codigo}, se encuentra al día.")
    
    p.setFont("Helvetica-Bold", 11)
    p.drawCentredString(width/2, 480, f"FECHA DE EMISIÓN: {timezone.now().strftime('%d/%m/%Y')}")
    p.drawCentredString(width/2, 460, "VALIDEZ: 30 DÍAS CALENDARIO")
    
    h = hashlib.sha256(f"SOL-{obj.id}-{timezone.now()}".encode()).hexdigest()[:12].upper()
    if obj.qr_code: p.drawImage(obj.qr_code.path, width/2-40, 250, width=80, height=80)
    p.setFont("Courier", 8); p.drawCentredString(width/2, 60, f"AUTENTICACIÓN_FINANCIERA: {h}")
    
    p.showPage(); p.save(); buffer.seek(0)
    return HttpResponse(buffer, content_type='application/pdf')

def pdf_notificacion_mora(request, nicho_id):
    obj = get_object_or_404(Nicho, id=nicho_id)
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    
    aplicar_estilo_seguridad(p, width, height, "AVISO DE COBRO Y MORA", colors.red)
    
    p.setFont("Helvetica-Bold", 12)
    p.drawString(70, 580, f"PROPIETARIO: {obj.propietario or 'N/A'}")
    p.setFont("Helvetica", 12)
    p.drawString(70, 560, f"Se le notifica que el nicho {obj.codigo} presenta un saldo de: Q{obj.monto_arbitrio}")
    p.drawString(70, 540, "Evite procesos de exhumación realizando su pago en Tesorería.")
    
    p.showPage(); p.save(); buffer.seek(0)
    return HttpResponse(buffer, content_type='application/pdf')

# --- CONSULTA PÚBLICA (QR) ---
def consulta_publica(request, codigo):
    nicho = get_object_or_404(Nicho, codigo=codigo)
    context = {
        'nicho': nicho,
        'esta_ocupado': bool(nicho.nombre_difunto),
        'es_moroso': nicho.monto_arbitrio <= 0,
        'fecha_consulta': timezone.now(),
    }
    return render(request, 'registros/consulta_inspector.html', context)

# --- REPORTE DE DAÑOS ---
def reportar_dano(request, nicho_id):
    nicho = get_object_or_404(Nicho, id=nicho_id)
    if request.method == 'POST':
        ReporteDano.objects.create(
            nicho=nicho,
            descripcion=request.POST.get('descripcion'),
            nivel_urgencia=request.POST.get('urgencia'),
            reportado_por=request.user.username if request.user.is_authenticated else "Público"
        )
        return redirect('consulta_publica', codigo=nicho.codigo)
    return render(request, 'registros/formulario_dano.html', {'nicho': nicho})

