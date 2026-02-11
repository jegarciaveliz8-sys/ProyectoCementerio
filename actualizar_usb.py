import os
import subprocess
from datetime import datetime

# --- CONFIGURACIÓN DE RUTAS ---
ORIGEN = os.getcwd()  # Tu carpeta actual en la PC
USB_PATH = '/media/usb'
FOLDER_CODIGO = os.path.join(USB_PATH, '01_CODIGO_SISTEMA')
FOLDER_BACKUP = os.path.join(USB_PATH, 'RESPALDO_SISTEMA')

def actualizar():
    fecha = datetime.now().strftime('%Y_%m_%d_%H%M%S')
    
    if not os.path.ismount(USB_PATH):
        print("❌ Error: La USB no está montada en /media/usb")
        return

    print(f"🚀 Iniciando actualización hacia la USB...")

    # 1. Sincronizar Código (Actualiza 01_CODIGO_SISTEMA)
    # Excluimos el entorno virtual y temporales para no llenar la USB de basura
    comando_rsync = [
        "rsync", "-av", "--delete",
        "--exclude", "venv_cementerio",
        "--exclude", "__pycache__",
        "--exclude", ".git",
        ORIGEN + "/", FOLDER_CODIGO
    ]
    
    try:
        print("📡 Actualizando código fuente...")
        subprocess.run(comando_rsync, check=True)
        
        # 2. Copiar Base de Datos con fecha a RESPALDO_SISTEMA
        db_destino = os.path.join(FOLDER_BACKUP, f'db_sanarate_{fecha}.sqlite3')
        subprocess.run(["cp", "db.sqlite3", db_destino], check=True)
        
        print(f"\n✨ ¡BRUTAL! Sistema actualizado y backup creado: db_sanarate_{fecha}.sqlite3")
    except Exception as e:
        print(f"⚠️ Error: {e}")

if __name__ == "__main__":
    actualizar()
