#!/bin/bash
echo "----------------------------------------------------"
echo "🛡️  INICIANDO SEGURO DE VIDA DE DATOS - SANARATE"
echo "----------------------------------------------------"

# Generar nombre con fecha y hora: backup_2026-01-24_09-40.sqlite3
FECHA=2026-01-24_09-39
NOMBRE_BACKUP="respaldos_diarios/backup_$FECHA.sqlite3"

# Hacer la copia de seguridad
cp db.sqlite3 $NOMBRE_BACKUP

echo "✅ Respaldo creado: $NOMBRE_BACKUP"
echo "🚀 Iniciando servidor en el puerto 8050..."
echo "----------------------------------------------------"

# Ejecutar el servidor de Django
python manage.py runserver 8050
