from django.shortcuts import render, redirect
from ..models.model_financiero import RegistroFinanciero
from ..models.model_calle import CalleRiesgo
from decimal import Decimal
import json

class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super().default(obj)

def dashboard_view(request):
    # --- PROCESAR ENVÍO DE FORMULARIOS ---
    if request.method == "POST":
        tipo_formulario = request.POST.get("tipo_formulario")
        
        if tipo_formulario == "financiero":
            RegistroFinanciero.objects.create(
                plataforma=request.POST.get("plataforma"),
                tipo_registro=request.POST.get("tipo_registro"),
                distancia_km=Decimal(request.POST.get("distancia_km", "0")),
                tiempo_minutos=int(request.POST.get("tiempo_minutos", "0")),
                monto_bruto=Decimal(request.POST.get("monto_bruto"))
            )
        elif tipo_formulario == "calle":
            CalleRiesgo.objects.create(
                colonia_o_zona=request.POST.get("colonia_o_zona"),
                tipo_riesgo=request.POST.get("tipo_riesgo"),
                descripcion=request.POST.get("descripcion"),
                latitud=Decimal(request.POST.get("latitud")),
                longitud=Decimal(request.POST.get("longitud"))
            )
        return redirect("dashboard")

    # --- CONSULTAR Y CALCULAR MÉTRICAS ---
    registros = RegistroFinanciero.objects.all()
    calles = CalleRiesgo.objects.all()

    total_bruto = Decimal('0.0')
    total_neto_viajes = Decimal('0.0')
    total_horas = Decimal('0.0')

    for reg in registros:
        total_bruto += reg.monto_bruto
        total_neto_viajes += reg.ganancia_neta_viaje
        if reg.tipo_registro == 'viaje':
            total_horas += Decimal(reg.tiempo_minutos) / Decimal('60.0')

    # Deducción de Renta Diaria fija ($1,900 / 6)
    renta_diaria = Decimal('1900.00') / Decimal('6.0')
    dinero_real_bolsillo = total_neto_viajes - renta_diaria

    # Convertimos los datos geográficos a JSON para Leaflet
    calles_lista = list(calles.values('colonia_o_zona', 'tipo_riesgo', 'descripcion', 'latitud', 'longitud'))
    calles_json = json.dumps(calles_lista, cls=DecimalEncoder)

    context = {
        'total_bruto': total_bruto,
        'dinero_real_bolsillo': dinero_real_bolsillo,
        'renta_diaria': renta_diaria,
        'total_horas': total_horas,
        'calles_peligrosas_json': calles_json,
    }
    return render(request, 'dashboard.html', context)
