from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponse
from django.db.models import Sum, Q, Count
from django.utils import timezone
from django.conf import settings
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.utils import simpleSplit
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
    p.setFont("Helvetica-Bold", 18)
    p.drawCentredString(width/2, 650, titulo)
    p.setFillColor(colors.black)

# --- VISTAS DE DASHBOARD Y MAPA ---
def dashboard(request):
    total = Nicho.objects.count()
    ocupados = Nicho.objects.exclude(Q(nombre_difunto__isnull=True) | Q(nombre_difunto="")).count()
    disponibles = total - ocupados
    mora_count = Nicho.objects.filter(monto_arbitrio__gt=0).exclude(nombre_difunto="").count()
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

# --- TÍTULO DE PROPIEDAD ---
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
    p.setFont("Courier-Bold", 10)
    p.drawCentredString(width/2, 450, f"COORDENADAS GIS: {obj.lat}, {obj.lng}")
    h = hashlib.sha256(f"TIT-{obj.id}-{obj.codigo}".encode()).hexdigest()[:16].upper()
    if obj.qr_code: p.drawImage(obj.qr_code.path, 460, 60, width=80, height=80)
    p.setFont("Courier", 8); p.setFillAlpha(0.5)
    p.drawString(60, 55, f"VERIFICACIÓN_TITULO: {h}"); p.setFillAlpha(1)
    p.showPage(); p.save(); buffer.seek(0)
    return HttpResponse(buffer, content_type='application/pdf')

# --- SOLVENCIA MUNICIPAL ---
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
    h = hashlib.sha256(f"SOL-{obj.id}".encode()).hexdigest()[:12].upper()
    if obj.qr_code: p.drawImage(obj.qr_code.path, width/2-40, 250, width=80, height=80)
    p.setFont("Courier", 8); p.drawCentredString(width/2, 60, f"AUTENTICACIÓN_FINANCIERA: {h}")
    p.showPage(); p.save(); buffer.seek(0)
    return HttpResponse(buffer, content_type='application/pdf')

# --- NOTIFICACIÓN DE MORA ---
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
    context = {'nicho': nicho, 'esta_ocupado': bool(nicho.nombre_difunto), 'es_moroso': nicho.monto_arbitrio > 0, 'fecha_consulta': timezone.now()}
    return render(request, 'registros/consulta_inspector.html', context)

# --- REPORTE DE DAÑOS ---
def reportar_dano(request, nicho_id):
    nicho = get_object_or_404(Nicho, id=nicho_id)
    if request.method == 'POST':
        ReporteDano.objects.create(nicho=nicho, descripcion=request.POST.get('descripcion'), nivel_urgencia=request.POST.get('urgencia'))
        return redirect('consulta_publica', codigo=nicho.codigo)
    return render(request, 'registros/formulario_dano.html', {'nicho': nicho})

# --- ACTA DE EXHUMACIÓN PROFESIONAL ---
def pdf_acta_exhumacion(request, nicho_id):
    obj = get_object_or_404(Nicho, id=nicho_id)
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    tipo_acta = request.GET.get('tipo', 'ADMINISTRATIVA').upper()
    dict_legales = {
        'JUDICIAL': ("ORDEN JUDICIAL / INVESTIGACIÓN", colors.red, "En cumplimiento a la orden judicial emitida por autoridad competente y bajo supervisión del Ministerio Público."),
        'FAMILIAR': ("SOLICITUD VOLUNTARIA DE FAMILIARES", colors.darkgreen, "A solicitud de los herederos legales, habiendo acreditado el parentesco y cancelado las tasas correspondientes."),
        'SANITARIA': ("PROTOCOLO DE SALUD PÚBLICA", colors.orange, "Por disposición de las autoridades de Salud Pública de conformidad con el Código de Salud."),
        'ADMINISTRATIVA': ("VENCIMIENTO DE ARRENDAMIENTO", colors.darkslategray, f"Debido al vencimiento del plazo de arrendamiento y falta de pago de arbitrios (Mora: Q{obj.monto_arbitrio}).")
    }
    titulo_doc, color_doc, base_legal = dict_legales.get(tipo_acta, dict_legales['ADMINISTRATIVA'])
    aplicar_estilo_seguridad(p, width, height, f"ACTA DE EXHUMACIÓN {tipo_acta}", color_doc)
    p.setFont("Helvetica-Bold", 13); p.drawCentredString(width/2, 620, f"ACTA No. {obj.numero_acta or 'SIN-NUMERO-2026'}")
    y_pos = 560
    p.setFont("Helvetica", 12)
    texto_intro = f"En el municipio de Sanarate, El Progreso, el Administrador del Cementerio hace constar la EXHUMACIÓN en el nicho {obj.codigo}."
    for line in simpleSplit(texto_intro, "Helvetica", 12, width-120):
        p.drawCentredString(width/2, y_pos, line); y_pos -= 18
    y_pos -= 10; p.setFont("Helvetica-Bold", 12); p.drawCentredString(width/2, y_pos, "IDENTIFICACIÓN DE LOS RESTOS:"); y_pos -= 20
    p.setFont("Helvetica", 11)
    for n_line in simpleSplit(obj.nombre_difunto or "S/N", "Helvetica", 11, 450):
        p.drawCentredString(width/2, y_pos, n_line); y_pos -= 15
    y_pos -= 20; p.setFont("Helvetica-Bold", 12); p.drawCentredString(width/2, y_pos, "FUNDAMENTACIÓN LEGAL:"); y_pos -= 20
    p.setFont("Helvetica-Oblique", 11)
    for l_line in simpleSplit(base_legal, "Helvetica-Oblique", 11, width-150):
        p.drawCentredString(width/2, y_pos, l_line); y_pos -= 15
    p.line(100, 180, 250, 180); p.drawCentredString(175, 165, "Administrador")
    p.line(width-250, 180, width-100, 180); p.drawCentredString(width-175, 165, "Registrador Municipal")
    h = hashlib.sha256(f"EXH-{obj.id}-{tipo_acta}".encode()).hexdigest()[:20].upper()
    p.setFont("Courier-Bold", 8); p.setFillAlpha(0.6); p.drawCentredString(width/2, 60, f"ID_VERIFICACIÓN: {h}")
    p.showPage(); p.save(); buffer.seek(0)
    return HttpResponse(buffer, content_type='application/pdf')

# --- ACTA DE EXHUMACIÓN PROFESIONAL (CONEXIÓN CON LIBRO DE ACTAS) ---
def pdf_acta_exhumacion(request, nicho_id):
    obj = get_object_or_404(Nicho, id=nicho_id)
    # Buscamos el registro más reciente en el Libro de Actas para este nicho
    acta_legal = obj.historial_actas.first() 
    
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    tipo_acta = request.GET.get('tipo', 'ADMINISTRATIVA').upper()
    
    # 1. Configuración de Textos según el Tipo
    dict_legales = {
        'JUDICIAL': (
            "ORDEN JUDICIAL / INVESTIGACIÓN", 
            colors.red, 
            f"En cumplimiento a la orden judicial y requerimiento del Ministerio Público, según acta de inspección ocular, para fines de investigación legal."
        ),
        'FAMILIAR': (
            "SOLICITUD VOLUNTARIA DE FAMILIARES", 
            colors.darkgreen, 
            "A solicitud expresa de los herederos o familiares cercanos, habiendo acreditado parentesco y responsabilidad civil sobre los restos."
        ),
        'SANITARIA': (
            "PROTOCOLO DE SALUD PÚBLICA", 
            colors.orange, 
            "Por disposición de las autoridades sanitarias y de conformidad con el Código de Salud por razones de higiene o riesgo epidemiológico."
        ),
        'ADMINISTRATIVA': (
            "VENCIMIENTO DE ARRENDAMIENTO", 
            colors.darkslategray, 
            f"Debido al vencimiento del plazo de arrendamiento perpetuo y falta de pago de arbitrios municipales (Mora acumulada: Q{obj.monto_arbitrio})."
        )
    }
    
    titulo_doc, color_doc, base_legal = dict_legales.get(tipo_acta, dict_legales['ADMINISTRATIVA'])
    aplicar_estilo_seguridad(p, width, height, f"ACTA DE EXHUMACIÓN {tipo_acta}", color_doc)
    
    # 2. Número de Acta y Encabezado
    num_acta = acta_legal.numero_acta if acta_legal else (obj.numero_acta or "SIN-NUMERO")
    p.setFont("Helvetica-Bold", 13)
    p.drawCentredString(width/2, 620, f"ACTA No. {num_acta}")
    
    y_pos = 580
    p.setFont("Helvetica", 11)
    
    # 3. Cuerpo del Acta - Datos del Proceso
    fecha_str = acta_legal.fecha_proceso.strftime('%d/%m/%Y a las %H:%M') if acta_legal else timezone.now().strftime('%d/%m/%Y')
    responsable = acta_legal.responsable_muni if acta_legal else "Administrador de Turno"
    
    intro = f"En la ciudad de Sanarate, El Progreso, siendo el {fecha_str}, ante el infrascrito {responsable}, se procede a realizar la exhumación de restos en el nicho código {obj.codigo}."
    
    for line in simpleSplit(intro, "Helvetica", 11, width-120):
        p.drawString(70, y_pos, line)
        y_pos -= 15

    # 4. Datos del Fallecido
    y_pos -= 10
    p.setFont("Helvetica-Bold", 11)
    p.drawString(70, y_pos, "DATOS DEL FALLECIDO:")
    p.setFont("Helvetica", 11)
    p.drawString(220, y_pos, f"{obj.nombre_difunto or 'Restos no identificados'}")
    
    # 5. Datos del Solicitante / Requirente
    y_pos -= 20
    p.setFont("Helvetica-Bold", 11)
    if tipo_acta == 'JUDICIAL':
        p.drawString(70, y_pos, "AUTORIDAD REQUERIENTE:")
        nombre_req = acta_legal.solicitante_nombre if acta_legal else "Ministerio Público / Organismo Judicial"
    else:
        p.drawString(70, y_pos, "NOMBRE DEL SOLICITANTE:")
        nombre_req = acta_legal.solicitante_nombre if acta_legal else "________________________________"
        
    p.setFont("Helvetica", 11)
    p.drawString(220, y_pos, f"{nombre_req}")
    
    y_pos -= 15
    p.setFont("Helvetica-Bold", 11)
    p.drawString(70, y_pos, "DPI / IDENTIFICACIÓN:")
    p.setFont("Helvetica", 11)
    dpi_req = acta_legal.solicitante_dpi if acta_legal else "________________________________"
    p.drawString(220, y_pos, f"{dpi_req}")

    # 6. Destino de los Restos
    y_pos -= 15
    p.setFont("Helvetica-Bold", 11)
    p.drawString(70, y_pos, "DESTINO FINAL:")
    p.setFont("Helvetica", 11)
    destino = acta_legal.destino_restos if acta_legal else (obj.notas_legales or "Osario General / Por definir")
    p.drawString(220, y_pos, f"{destino}")

    # 7. Fundamentación Legal
    y_pos -= 30
    p.setFont("Helvetica-Bold", 11)
    p.drawString(70, y_pos, "FUNDAMENTACIÓN Y OBSERVACIONES:")
    y_pos -= 15
    p.setFont("Helvetica-Oblique", 10)
    obs = acta_legal.observaciones_legales if acta_legal and acta_legal.observaciones_legales else base_legal
    for l_line in simpleSplit(obs, "Helvetica-Oblique", 10, width-140):
        p.drawString(70, y_pos, l_line)
        y_pos -= 14

    # 8. Firmas
    p.line(100, 150, 260, 150)
    p.drawCentredString(180, 135, "F. Responsable Municipal")
    p.setFont("Helvetica", 8)
    p.drawCentredString(180, 125, f"{responsable}")
    
    p.line(width-260, 150, width-100, 150)
    p.setFont("Helvetica", 11)
    p.drawCentredString(width-180, 135, "F. Quien Recibe / Autoridad")
    p.setFont("Helvetica", 8)
    p.drawCentredString(width-180, 125, f"{nombre_req}")

    # Pie de página con seguridad
    h = hashlib.sha256(f"EXH-{obj.id}-{tipo_acta}-{num_acta}".encode()).hexdigest()[:20].upper()
    p.setFont("Courier-Bold", 8)
    p.setFillAlpha(0.6)
    p.drawCentredString(width/2, 50, f"DOCUMENTO OFICIAL MUNICIPALIDAD DE SANARATE - HASH: {h}")
    
    p.showPage()
    p.save()
    buffer.seek(0)
    return HttpResponse(buffer, content_type='application/pdf')

