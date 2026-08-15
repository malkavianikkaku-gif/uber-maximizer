from django.db import models
from django.contrib.auth.models import User

class CalleRiesgo(models.Model):

    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='calles', null=True, blank=True)

    OPCIONES_RIESGO = [
        ('inclinacion', 'Inclinación Extrema'),
        ('terraceria', 'Terracería / Baches'),
        ('infraestructura', 'Tope Rompe-Cárter / Inundación'),
    ]

    colonia_o_zona = models.CharField(max_length=100)
    tipo_riesgo = models.CharField(max_length=50, choices=OPCIONES_RIESGO)
    descripcion = models.TextField()
    latitud = models.DecimalField(max_digits=9, decimal_places=6, default=19.432608)
    longitud = models.DecimalField(max_digits=9, decimal_places=6, default=-99.133208)
    fecha_reporte = models.DateTimeField(auto_now_add=True)

    activo = models.BooleanField(default=True)

    class Meta:
        db_table = 'core_calleriesgo'

    def __str__(self):
        return f"⚠️ {self.tipo_riesgo} en {self.colonia_o_zona}"
