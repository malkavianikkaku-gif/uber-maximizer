from django.contrib import admin
from ..models.model_calle import CalleRiesgo


@admin.register(CalleRiesgo)
class CalleRiesgoAdmin(admin.ModelAdmin):
    list_display = ('colonia_o_zona', 'tipo_riesgo', 'fecha_reporte')
    list_filter = ('tipo_riesgo',)
