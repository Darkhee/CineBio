from django.urls import path
from . import views


urlpatterns = [
    path('', views.listar_peliculas, name='listar_peliculas'),
    path('pelicula/<int:id>/', views.detalle_pelicula, name='detalle_pelicula'),
    path('registro/', views.registro, name='registro'),
    path('login/', views.login_usuario, name='login'),
    path('logout/', views.logout_usuario, name='logout'),
    path('funcion/<int:funcion_id>/butacas/', views.seleccionar_butacas, name='seleccionar_butacas'),
    path('funcion/<int:funcion_id>/confirmar/', views.confirmar_butacas, name='confirmar_butacas'),
    path('confiteria/', views.confiteria, name='confiteria'),
    path('pago/', views.pago, name='pago'),
    path('confirmacion/<int:compra_id>/', views.confirmacion, name='confirmacion'),
    path('perfil/', views.perfil, name='perfil'),
]