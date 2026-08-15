from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import login
from ..models.model_perfil import PerfilConductor
from decimal import Decimal

def registro_view(request):
    if request.method == "POST":
        data = request.POST
        
        # 1. Creamos el usuario base de Django
        usuario = User.objects.create_user(
            username=data.get("username"),
            password=data.get("password")
        )
        
        # 2. Creamos su perfil de conductor enlazado con sus costos dinámicos
        PerfilConductor.objects.create(
            usuario=usuario,
            modelo_carro=data.get("modelo_carro"),
            rendimiento_km_litro=Decimal(data.get("rendimiento")),
            costo_gasolina_litro=Decimal(data.get("costo_gasolina")),
            renta_semanal=Decimal(data.get("renta_semanal"))
        )
        
        # 3. Iniciamos su sesión automáticamente y lo mandamos al dashboard
        login(request, usuario)
        return redirect("dashboard")
        
    return render(request, "registro.html")
