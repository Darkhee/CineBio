from django.urls import path
from . import views

app_name = 'portal_admin'

urlpatterns = [
    path('', views.login_admin, name='login'),
    path('salir/', views.logout_admin, name='logout'),
    path('inicio/', views.dashboard, name='dashboard'),
    path('peliculas/', views.peliculas_list, name='peliculas_list'),
    path('peliculas/nueva/', views.pelicula_create, name='pelicula_create'),
    path('peliculas/<int:pk>/editar/', views.pelicula_edit, name='pelicula_edit'),
    path('peliculas/<int:pk>/eliminar/', views.pelicula_delete, name='pelicula_delete'),
    path('funciones/', views.funciones_list, name='funciones_list'),
    path('funciones/nueva/', views.funcion_create, name='funcion_create'),
    path('funciones/<int:pk>/editar/', views.funcion_edit, name='funcion_edit'),
    path('funciones/<int:pk>/eliminar/', views.funcion_delete, name='funcion_delete'),
    path('productos/', views.productos_list, name='productos_list'),
    path('productos/nuevo/', views.producto_create, name='producto_create'),
    path('productos/<int:pk>/editar/', views.producto_edit, name='producto_edit'),
    path('productos/<int:pk>/eliminar/', views.producto_delete, name='producto_delete'),  
    path('ventas/', views.ventas_list, name='ventas_list'),
    path('ventas/<int:compra_id>/', views.venta_detalle, name='venta_detalle'),
    path('ventas/<int:compra_id>/devolver/', views.procesar_devolucion, name='procesar_devolucion'),
    path('usuarios/', views.usuarios_list, name='lista_usuarios'),
    path('butacas/', views.butacas_salas, name='butacas_salas'),
    path('butacas/<int:sala_id>/', views.butacas_sala_detalle, name='butacas_sala_detalle'),
]