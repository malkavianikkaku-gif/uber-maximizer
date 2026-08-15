from django.db import models
from decimal import Decimal
from django.contrib.auth.models import User

class RegistroFinanciero(models.Model):

    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='registros', null=True, blank=True)

    OPCIONES_TIPO = [
        ('viaje', 'Viaje Regular'),
        ('bono', 'Bono o Incentivo'),
    ]
    
    plataforma = models.CharField(max_length=30)
    tipo_registro = models.CharField(max_length=20, choices=OPCIONES_TIPO)
    distancia_km = models.DecimalField(max_digits=6, decimal_places=2, default=0.0)
    tiempo_minutos = models.IntegerField(default=0)
    monto_bruto = models.DecimalField(max_digits=8, decimal_places=2)
    
    gasto_gasolina = models.DecimalField(max_digits=8, decimal_places=2, default=0.0, editable=False)
    gasto_desgaste = models.DecimalField(max_digits=8, decimal_places=2, default=0.0, editable=False)
    impuestos_sat = models.DecimalField(max_digits=8, decimal_places=2, default=0.0, editable=False)
    ganancia_neta_viaje = models.DecimalField(max_digits=8, decimal_places=2, default=0.0, editable=False)
    
    fecha_registro = models.DateTimeField(auto_now_add=True)

    activo = models.BooleanField(default=True)

    class Meta:
        # Esto le dice a Django que mantenga el nombre interno original de la tabla en la base de datos
        db_table = 'core_registrofinanciero'

    def __str__(self):
        return f"{self.plataforma} - {self.tipo_registro} (${self.monto_bruto})"

    def save(self, *args, **kwargs):
        rendimiento = Decimal('14.0')
        precio_gasolina = Decimal('24.50')
        costo_gasolina_km = precio_gasolina / rendimiento
        costo_desgaste_km = Decimal('0.40')

        if self.tipo_registro == 'viaje':
            self.gasto_gasolina = self.distancia_km * costo_gasolina_km
            self.gasto_desgaste = self.distancia_km * costo_desgaste_km
            self.impuestos_sat = self.monto_bruto * Decimal('0.031')
            self.ganancia_neta_viaje = self.monto_bruto - self.gasto_gasolina - self.gasto_desgaste - self.impuestos_sat
        elif self.tipo_registro == 'bono':
            self.gasto_gasolina = Decimal('0.0')
            self.gasto_desgaste = Decimal('0.0')
            self.impuestos_sat = self.monto_bruto * Decimal('0.021')
            self.ganancia_neta_viaje = self.monto_bruto - self.impuestos_sat

        super().save(*args, **kwargs)
