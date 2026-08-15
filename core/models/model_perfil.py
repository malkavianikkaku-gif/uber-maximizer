from django.db import models
from django.contrib.auth.models import User
from decimal import Decimal

class PerfilConductor(models.Model):
    # Conectamos cada perfil a un usuario único de Django
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil')
    
    # Datos dinámicos del auto que antes estaban fijos
    modelo_carro = models.CharField(max_length=50, default="Chevrolet Spark 2016")
    rendimiento_km_litro = models.DecimalField(max_digits=4, decimal_places=1, default=Decimal('14.0'))
    costo_gasolina_litro = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('24.50'))
    renta_semanal = models.DecimalField(max_digits=7, decimal_places=2, default=Decimal('1900.00'))
    
    # Costo por kilómetro calculado dinámicamente para este usuario
    costo_desgaste_km = models.DecimalField(max_digits=4, decimal_places=2, default=Decimal('0.40'))

    class Meta:
        db_table = 'core_perfilconductor'

    def __str__(self):
        return f"Perfil de {self.usuario.username} ({self.modelo_carro})"
