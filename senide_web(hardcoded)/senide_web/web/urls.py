from django.urls import include, path
from web import views

urlpatterns = [
    path(r"", views.home, name="home"),
    path(r"transcripciones/<str:usuario>/", views.transcripciones, name="transcripciones"),
    path(r"perfil/<str:usuario>/", views.perfil, name="perfil"),
    path(r"estadisticas/<str:usuario>/", views.estadisticas, name="estadisticas"),
]