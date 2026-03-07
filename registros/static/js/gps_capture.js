function captureGPS(nichoId) {
    if (!navigator.geolocation) {
        alert("Tu navegador no soporta GPS");
        return;
    }

    // Cambiar el texto del botón para saber que está trabajando
    const btn = document.getElementById(`btn-gps-${nichoId}`);
    const originalText = btn.innerText;
    btn.innerText = "🛰️ Buscando...";
    btn.disabled = true;

    navigator.geolocation.getCurrentPosition(
        (position) => {
            const lat = position.coords.latitude;
            const lng = position.coords.longitude;

            // Enviar los datos a Django mediante una petición rápida (fetch)
            fetch(`/admin/registros/nicho/${nichoId}/set_gps/?lat=${lat}&lng=${lng}`)
                .then(response => {
                    if (response.ok) {
                        alert(`¡Ubicación guardada!\nLat: ${lat}\nLng: ${lng}`);
                        location.reload(); // Recarga para ver los cambios
                    } else {
                        alert("Error al guardar en la base de datos");
                        btn.innerText = originalText;
                        btn.disabled = false;
                    }
                });
        },
        (error) => {
            alert("Error: Asegúrate de activar el GPS y dar permisos.");
            btn.innerText = originalText;
            btn.disabled = false;
        },
        { enableHighAccuracy: true }
    );
}
