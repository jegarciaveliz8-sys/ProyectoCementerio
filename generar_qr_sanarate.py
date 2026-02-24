import qrcode
from PIL import Image

# Configuración
dominio_ngrok = "https://uninferentially-fibrillar-ward.ngrok-free.dev"
nicho_ejemplo = "SEC-A-101" # Cambia esto por un código real que tengas
url = f"{dominio_ngrok}/nicho/{nicho_ejemplo}/"

print(f"--- Generador de QR Sanarate ---")
print(f"Generando para: {url}")

# Crear el QR
qr = qrcode.QRCode(
    version=1,
    error_correction=qrcode.constants.ERROR_CORRECT_L,
    box_size=10,
    border=4,
)
qr.add_data(url)
qr.make(fit=True)

# Crear imagen y guardarla
img = qr.make_image(fill_color="black", back_color="white")
img.save("codigo_qr_presentacion.png")

print("✅ ARCHIVO CREADO: codigo_qr_presentacion.png")
