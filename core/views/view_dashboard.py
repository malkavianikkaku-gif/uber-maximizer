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

    if request.method == "POST":
        tipo_formulario = request.POST.get("tipo_formulario")
        
        if tipo_formulario == "financiero":
            # ... (Tu código de guardado financiero se queda igual) ...
            RegistroFinanciero.objects.create(
                plataforma=request.POST.get("plataforma"),
                tipo_registro=request.POST.get("tipo_registro"),
                distancia_km=Decimal(request.POST.get("distancia_km", "0")),
                tiempo_minutos=int(request.POST.get("tiempo_minutos", "0")),
                monto_bruto=Decimal(request.POST.get("monto_bruto"))
            )
        elif tipo_formulario == "calle":
            # ... (Tu código de guardado de calles se queda igual) ...
            CalleRiesgo.objects.create(
                colonia_o_zona=request.POST.get("colonia_o_zona"),
                tipo_riesgo=request.POST.get("tipo_riesgo"),
                descripcion=request.POST.get("descripcion"),
                latitud=Decimal(request.POST.get("latitud")),
                longitud=Decimal(request.POST.get("longitud"))
            )
            
        # 🌟 NUEVA ACCIÓN: ARCHIVAR JORNADA TOTAL
        elif tipo_formulario == "cierre_jornada":
            # Cambiamos masivamente el estatus a False en PostgreSQL
            RegistroFinanciero.objects.filter(activo=True).update(activo=False)
            CalleRiesgo.objects.filter(activo=True).update(activo=False)
            return redirect("dashboard")
            
        return redirect("dashboard")

    # 🌟 CORRECCIÓN: Filtramos las consultas para que SOLO traigan lo activo hoy
    registros = RegistroFinanciero.objects.filter(activo=True)
    calles = CalleRiesgo.objects.filter(activo=True)

    # ... (Todo tu bloque intermedio de cálculos financieros con 'global_neto_viajes',
    # 'apps_info' y serialización JSON se queda exactamente igual) ...
    global_bruto = Decimal('0.0')
    global_neto_viajes = Decimal('0.0')
    global_horas = Decimal('0.0')


    apps_info = {
        'Uber': {'bruto': Decimal('0.0'), 'neto': Decimal('0.0'), 'horas': Decimal('0.0'), 'viajes': 0},
        'Didi': {'bruto': Decimal('0.0'), 'neto': Decimal('0.0'), 'horas': Decimal('0.0'), 'viajes': 0},
        'InDrive': {'bruto': Decimal('0.0'), 'neto': Decimal('0.0'), 'horas': Decimal('0.0'), 'viajes': 0},
    }

    for reg in registros:
        app = reg.plataforma
        if app in apps_info:
            apps_info[app]['bruto'] += reg.monto_bruto
            apps_info[app]['neto'] += reg.ganancia_neta_viaje

            global_bruto += reg.monto_bruto
            global_neto_viajes += reg.ganancia_neta_viaje

            if reg.tipo_registro == 'viaje':
                horas_viaje = Decimal(reg.tiempo_minutos) / Decimal('60.0')
                apps_info[app]['horas'] += horas_viaje
                apps_info[app]['viajes'] += 1
                global_horas += horas_viaje
       # Deducción de Renta Diaria fija ($1,900 / 6)
    renta_diaria = Decimal('1900.00') / Decimal('6.0')
    dinero_real_bolsillo = global_neto_viajes - renta_diaria

    # ... (Tu código anterior de sumatoria de totales se queda igual) ...

    # Deducción de Renta Diaria fija ($1,900 / 6)
    renta_diaria = Decimal('1900.00') / Decimal('6.0')
    dinero_real_bolsillo = global_neto_viajes - renta_diaria


    if global_neto_viajes > 0:

        porcentaje_equilibrio = (global_neto_viajes / renta_diaria) * Decimal('100.0')
        porcentaje_equilibrio = min(porcentaje_equilibrio, Decimal('100.0'))
    else:
        porcentaje_equilibrio = Decimal('0.0')


    pesos_faltantes_renta = max(Decimal('0.0'), renta_diaria - global_neto_viajes)

    for app, data in apps_info.items():
        data['salario_x_hora'] = data['neto'] / data['horas'] if data['horas'] > 0 else Decimal('0.0')

    calles_lista = list(calles.values('colonia_o_zona', 'tipo_riesgo', 'descripcion', 'latitud', 'longitud'))
    calles_json = json.dumps(calles_lista, cls=DecimalEncoder)


    context = {
        'total_bruto': global_bruto,
        'dinero_real_bolsillo': dinero_real_bolsillo,
        'renta_diaria': renta_diaria,
        'total_horas': global_horas,
        'apps_info': apps_info,
        'calles_peligrosas_json': calles_json,
        'porcentaje_equilibrio': float(porcentaje_equilibrio),
        'pesos_faltantes_renta': pesos_faltantes_renta,
    }
    return render(request, 'dashboard.html', context)

