from registros.models import Nicho
pabellones = {
    "Sector A": {"inicio": (14.783180, -90.204650), "ancho": 12, "sep_v": 0.000018, "sep_h": 0.000022},
    "Sector B": {"inicio": (14.782600, -90.205200), "ancho": 6,  "sep_v": 0.000025, "sep_h": 0.000020},
    "Sector C": {"inicio": (14.783550, -90.204000), "ancho": 10, "sep_v": 0.000015, "sep_h": 0.000025},
    "Sector D": {"inicio": (14.782250, -90.204300), "ancho": 8,  "sep_v": 0.000020, "sep_h": 0.000022},
}
actualizados = []
for nombre, data in pabellones.items():
    nichos = Nicho.objects.filter(nivel__sector__nombre=nombre)
    ini = data["inicio"]
    for i, n in enumerate(nichos):
        fila = i // data["ancho"]
        col = i % data["ancho"]
        n.latitud = ini[0] - (fila * data["sep_v"])
        n.longitud = ini[1] + (col * data["sep_h"])
        actualizados.append(n)
if actualizados:
    Nicho.objects.bulk_update(actualizados, ['latitud', 'longitud'])
    print(f"✅ EXITO: {len(actualizados)} nichos ubicados en Sanarate.")
