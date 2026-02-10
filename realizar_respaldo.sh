#!/bin/bash
# Ir a la carpeta del proyecto
cd /home/jose/ProyectoCementerio
# Activar el entorno virtual
source venv_cementerio/bin/activate
# Crear nombre de archivo con fecha
FECHA=$(date +"%Y-%m-%d")
# Exportar datos
python3 manage.py dumpdata > respaldos/backup_$FECHA.json
echo "Respaldo completado: backup_$FECHA.json"
