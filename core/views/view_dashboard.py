from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from ..models.model_financiero import RegistroFinanciero
from ..models.model_calle import CalleRiesgo
from decimal import Decimal
import json

class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super().default(obj)

# 🌟 AGREGAMOS ESTE DECORADOR: Protege la pantalla para que solo entren usuarios firmados
@login_required(login_url='registro')
def dashboard_view(request):
    # 1. Recuperamos el perfil dinámico del conductor que inició sesión
    perfil = request.user.perfil
    
    # --- PROCESAR ENVÍO DE FORMULARIOS ---
    if request.method == "POST":
        tipo_formulario = request.POST.get("tipo_formulario")
        
        if tipo_formulario == "financiero":
            # 🌟 MODIFICACIÓN: Guardamos vinculando el viaje al usuario actual
            tiempo_recibido = request.POST.get("tiempo_minutos", "0")
            tiempo_minutos_limpio = int(Decimal(tiempo_recibido)) if '.' in tiempo_recibido else int(tiempo_recibido)
            RegistroFinanciero.objects.create(
                usuario=request.user,
                plataforma=request.POST.get("plataforma"),
                tipo_registro=request.POST.get("tipo_registro"),
                distancia_km=Decimal(request.POST.get("distancia_km", "0")),
                tiempo_minutos=int(request.POST.get("tiempo_minutos", "0")),
                monto_bruto=Decimal(request.POST.get("monto_bruto"))
            )
        elif tipo_formulario == "calle":
            # 🌟 MODIFICACIÓN: Guardamos vinculando la calle al usuario actual
            CalleRiesgo.objects.create(
                usuario=request.user,
                colonia_o_zona=request.POST.get("colonia_o_zona"),
                tipo_riesgo=request.POST.get("tipo_riesgo"),
                descripcion=request.POST.get("descripcion"),
                latitud=Decimal(request.POST.get("latitud")),
                longitud=Decimal(request.POST.get("longitud"))
            )

        elif tipo_formulario == "cierre_jornada":
            # 🌟 MODIFICACIÓN: Solo archivamos los viajes del usuario actual
            RegistroFinanciero.objects.filter(usuario=request.user, activo=True).update(activo=False)
            CalleRiesgo.objects.filter(usuario=request.user, activo=True).update(activo=False)
            return redirect("dashboard")
            
        return redirect("dashboard")

    # --- CONSULTAR Y CALCULAR MÉTRICAS DINÁMICAS ---
    # 🌟 FILTRAMOS LAS CONSULTAS: Solo traemos los datos de este conductor específico
    registros = RegistroFinanciero.objects.filter(usuario=request.user, activo=True)
    calles = CalleRiesgo.objects.filter(usuario=request.user, activo=True)

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

    # 🌟 CÁLCULO TOTALMENTE DINÁMICO: Consumimos la renta semanal del perfil del usuario
    renta_diaria = perfil.renta_semanal / Decimal('6.0')
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
        'modelo_carro': perfil.modelo_carro, # Pasamos el auto para mostrarlo en el título
    }

    return render(request, 'dashboard.html', context)

