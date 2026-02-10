#!/bin/bash
# Crear carpeta de respaldos si no existe
mkdir -p respaldos
FECHA=$(date +"%d-%m-%Y_%H-%M")
# Guardar toda la base de datos de Django en JSON
python3 manage.py dumpdata > respaldos/respaldo_sanarate_$FECHA.json
echo "✅ Respaldo guardado como: respaldos/respaldo_sanarate_$FECHA.json"
