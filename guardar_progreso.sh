#!/bin/bash
FECHA=$(date +"%Y-%m-%d_%H-%M")
mkdir -p respaldos_diarios
echo "📦 Respaldando base de datos..."
cp db.sqlite3 "respaldos_diarios/backup_sanarate_$FECHA.sqlite3"
echo "✅ Guardado en respaldos_diarios/backup_sanarate_$FECHA.sqlite3"
git add .
git commit -m "Respaldo automático $FECHA"
echo "🚀 Todo sincronizado."
