from django.contrib import admin
from ..models.model_financiero import RegistroFinanciero


@admin.register(RegistroFinanciero)
class RegistroFinancieroAdmin(admin.ModelAdmin):
    list_display = ('plataforma', 'tipo_registro', 'monto_bruto', 'ganancia_neta_viaje', 'fecha_registro')
    list_filter = ('plataforma', 'tipo_registro')
    readonly_fields = ('gasto_gasolina', 'gasto_desgaste', 'impuestos_sat', 'ganancia_neta_viaje')
