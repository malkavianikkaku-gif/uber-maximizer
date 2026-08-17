from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from ..models.model_financiero import RegistroFinanciero
from ..models.model_calle import CalleRiesgo
from decimal import Decimal
from django.utils import timezone
from datetime import timedelta
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
    filtro_tiempo = request.GET.get('filtro','hoy')  # Por defecto, mostrar solo los registros de hoy
    registros = RegistroFinanciero.objects.filter(usuario=request.user, activo=True)
    calles = CalleRiesgo.objects.filter(usuario=request.user, activo=True)
    ahora = timezone.now()

    if filtro_tiempo == 'hoy':
        registros = registros.filter(activo=True)
        calles = calles.filter(activo=True)
    elif filtro_tiempo == 'semana':
        hace_una_semana = ahora - timedelta(days=7)  # Lunes de esta semana
        registros = registros.filter(fecha_registro__gte=hace_una_semana)
        calles = calles.filter(fecha_reporte__gte=hace_una_semana)
    elif filtro_tiempo == 'mes':
        hace_un_mes = ahora - timedelta(days=30)  # Aproximadamente un mes atrás
        registros = registros.filter(fecha_registro__gte=hace_un_mes)
        calles = calles.filter(fecha_reporte__gte=hace_un_mes)

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
    if filtro_tiempo == 'hoy':
        renta_calculada = perfil.renta_semanal / Decimal('6.0')  # Renta diaria
    elif filtro_tiempo == 'semana':
        renta_calculada = perfil.renta_semanal  # Renta semanal
    elif filtro_tiempo == 'mes':
        renta_calculada = perfil.renta_semanal * Decimal('4.0')  # Renta mensual

    dinero_real_bolsillo = global_neto_viajes - renta_calculada


    if global_neto_viajes > 0:

        porcentaje_equilibrio = (global_neto_viajes / renta_calculada) * Decimal('100.0')
        porcentaje_equilibrio = min(porcentaje_equilibrio, Decimal('100.0'))
    else:

        porcentaje_equilibrio = Decimal('0.0')


    pesos_faltantes_renta = max(Decimal('0.0'), renta_calculada - global_neto_viajes)

    for app, data in apps_info.items():
        data['salario_x_hora'] = data['neto'] / data['horas'] if data['horas'] > 0 else Decimal('0.0')

    apps_brutos = [float(apps_info['Uber']['bruto']), float(apps_info['Didi']['bruto']), float(apps_info['InDrive']['bruto'])]
    apps_netos = [float(apps_info['Uber']['neto']), float(apps_info['Didi']['neto']), float(apps_info['InDrive']['neto'])]
    apps_salarios_hora = [float(apps_info['Uber']['salario_x_hora']), float(apps_info['Didi']['salario_x_hora']), float(apps_info['InDrive']['salario_x_hora'])]
    apps_nombres = ['Uber', 'Didi', 'InDrive']

    calles_lista = list(calles.values('colonia_o_zona', 'tipo_riesgo', 'descripcion', 'latitud', 'longitud'))
    calles_json = json.dumps(calles_lista, cls=DecimalEncoder)

    apps_nombres = ['Uber', 'Didi', 'InDrive']


    apps_salarios_hora = [
        float(apps_info.get(app, {}).get('salario_x_hora', Decimal('0.0')) or 0.0) for app in apps_nombres
    ]


    context = {
        'total_bruto': global_bruto,
        'dinero_real_bolsillo': dinero_real_bolsillo,
        'renta_calculada': renta_calculada,
        'total_horas': global_horas,
        'apps_info': apps_info,
        'calles_peligrosas_json': calles_json,
        'porcentaje_equilibrio': float(porcentaje_equilibrio),
        'pesos_faltantes_renta': pesos_faltantes_renta,
        'modelo_carro': perfil.modelo_carro, # Pasamos el auto para mostrarlo en el título
        'apps_nombres_json': json.dumps(apps_nombres),
        'apps_salarios_hora_json': json.dumps(apps_salarios_hora)
    }

    return render(request, 'dashboard.html', context)

