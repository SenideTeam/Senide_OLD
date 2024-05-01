from django.shortcuts import render

def home(request):
    if request.method == "POST":
        contraseña = request.POST.get("password", None)
        if contraseña == "Admin123":
            usuario = request.POST.get("username", None)
    return render(request, "web/index.html", locals())

def transcripciones(request, usuario):
    usuario = usuario
    return render(request, "web/transcripciones.html", locals())

def perfil(request, usuario):
    usuario = usuario
    return render(request, "web/perfil.html", locals())

def estadisticas(request, usuario):
    usuario = usuario
    return render(request, "web/estadisticas.html", locals())