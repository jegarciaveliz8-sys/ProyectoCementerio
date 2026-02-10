#!/bin/bash
ORIGEN="$HOME/ProyectoCementerio/db.sqlite3"
DESTINO="/mnt/sanarate/RESPALDO_SISTEMA"

echo "🔄 Iniciando respaldo de seguridad con permisos de administrador..."

# Usamos sudo para crear la carpeta y copiar
sudo mkdir -p $DESTINO
FECHA=$(date +"%d-%m-%Y_%H-%M")

if sudo cp $ORIGEN "$DESTINO/db_backup_$FECHA.sqlite3" && sudo cp $ORIGEN "$DESTINO/db_actual.sqlite3"; then
    sudo sync
    echo "-------------------------------------------"
    echo "✅ ¡ÉXITO! Los datos están seguros en la USB."
    echo "📅 Archivo: db_backup_$FECHA.sqlite3"
    echo "-------------------------------------------"
else
    echo "❌ ERROR: No se pudo realizar el respaldo."
    echo "Revisa si la USB está conectada en /mnt/sanarate"
fi
