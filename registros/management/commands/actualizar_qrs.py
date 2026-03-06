from django.core.management.base import BaseCommand
from registros.models import Nicho

class Command(BaseCommand):
    help = 'Actualiza todos los QRs de forma masiva'

    def handle(self, *args, **options):
        # Filtramos solo los que tienen nombre para que sea instantáneo
        nichos = Nicho.objects.exclude(nombre_difunto__isnull=True).exclude(nombre_difunto='')
        total = nichos.count()
        self.stdout.write(self.style.NOTICE(f"🚀 Sincronizando {total} nichos con datos..."))
        
        for i, n in enumerate(nichos, 1):
            n.save()
            if i % 10 == 0:
                self.stdout.write(f"✅ {i}/{total} procesados...")
        
        self.stdout.write(self.style.SUCCESS('✨ ¡TODOS LOS QRS ACTUALIZADOS CON ÉXITO!'))
