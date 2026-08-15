"""
URL configuration for uber_maximizer_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from core.views.view_dashboard import dashboard_view  # <-- Importamos tu nueva vista del tablero
from core.views.view_historial import historial_view
from core.views.view_registro import registro_view  # <-- Importamos tu nueva vista de registro
from core.views.view_auth import login_view, logout_view  # <-- Importamos tu nueva vista de autenticación
    
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', dashboard_view, name='dashboard'),
    path('historial/', historial_view, name='historial'),
    path('registro/', registro_view, name='registro'),
    path('login/', login_view, name='login'),  # <-- Agregamos la ruta para la vista de login
    path('logout/', logout_view, name='logout'),  # <-- Agregamos la
]

