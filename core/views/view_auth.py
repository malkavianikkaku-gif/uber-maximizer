from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout

def login_view(request):
    if request.method == "POST":
        usuario_txt = request.POST.get("username")
        contra_txt = request.POST.get("password")
        
        # Validamos las credenciales contra PostgreSQL de forma segura
        user = authenticate(request, username=usuario_txt, password=contra_txt)
        
        if user is not None:
            login(request, user)
            return redirect("dashboard")
        else:
            # Si fallan los datos, recargamos con la alerta de error
            return render(request, "login.html", {"error": True})
            
    return render(request, "login.html")

def logout_view(request):
    logout(request)
    return redirect("login")
