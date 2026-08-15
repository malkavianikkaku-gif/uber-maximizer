from django.shortcuts import render
from ..models.model_financiero import RegistroFinanciero
from ..models.model_calle import CalleRiesgo
from decimal import Decimal
from collections import defaultdict

def historial_view(request):
    # 1. Consultamos de PostgreSQL solo los registros del pasado (archivados)
    viajes_archivados = RegistroFinanciero.objects.filter(activo=False).order_by('-fecha_registro')
    calles_archivadas = CalleRiesgo.objects.filter(activo=False).order_by('-fecha_reporte')

    # 2. Agrupamos los viajes por día utilizando un diccionario para hacer la matemática ejecutiva
    jornadas_historicas = defaultdict(lambda: {
        'bruto': Decimal('0.0'),
        'neto_viajes': Decimal('0.0'),
        'horas': Decimal('0.0'),
        'viajes_count': 0,
        'detalles_apps': defaultdict(lambda: {'bruto': Decimal('0.0'), 'viajes': 0})
    })

    for reg in viajes_archivados:
        # Extraemos la fecha en formato YYYY-MM-DD para usarla como clave
        fecha_str = reg.fecha_registro.strftime('%Y-%m-%d')
        
        jornadas_historicas[fecha_str]['bruto'] += reg.monto_bruto
        jornadas_historicas[fecha_str]['neto_viajes'] += reg.ganancia_neta_viaje
        jornadas_historicas[fecha_str]['viajes_count'] += 1
        
        # Desglose interno por aplicación por cada día pasado
        app = reg.plataforma
        jornadas_historicas[fecha_str]['detalles_apps'][app]['bruto'] += reg.monto_bruto
        jornadas_historicas[fecha_str]['detalles_apps'][app]['viajes'] += 1

        if reg.tipo_registro == 'viaje':
            jornadas_historicas[fecha_str]['horas'] += Decimal(reg.tiempo_minutos) / Decimal('60.0')

    # 3. Formateamos los datos calculados para que Django los lea de forma limpia en el HTML
    reporte_final = []
    renta_diaria = Decimal('1900.00') / Decimal('6.0')  # Tu cuota fija real del Spark

    for fecha, datos in jornadas_historicas.items():
        # Restamos la renta diaria fija a cada jornada pasada
        neto_real_bolsillo = datos['neto_viajes'] - renta_diaria
        
        reporte_final.append({
            'fecha': fecha,
            'bruto': datos['bruto'],
            'neto_bolsillo': neto_real_bolsillo,
            'horas': datos['horas'],
            'viajes_count': datos['viajes_count'],
            'apps': dict(datos['detalles_apps'])
        })

    context = {
        'historial_jornadas': reporte_final,
        'renta_diaria': renta_diaria,
        'calles_reportadas': calles_archivadas
    }
    
    return render(request, 'historial.html', context)
