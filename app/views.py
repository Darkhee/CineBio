from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from .models import Pelicula, Funcion, Butaca, ProductoConfiteria, Compra, Entrada, ItemConfiteria, PerfilUsuario


def listar_peliculas(request):
    peliculas = Pelicula.objects.all()
    return render(request, 'app/listar_peliculas.html', {
        'peliculas': peliculas
    })


def detalle_pelicula(request, id):
    pelicula = Pelicula.objects.get(id=id)
    funciones = Funcion.objects.filter(pelicula=pelicula)
    
    funciones_por_tipo = {}
    for funcion in funciones:
        tipo = funcion.get_tipo_display()
        if tipo not in funciones_por_tipo:
            funciones_por_tipo[tipo] = []
        funciones_por_tipo[tipo].append(funcion)
    
    return render(request, 'app/detalle_pelicula.html', {
        'pelicula': pelicula,
        'funciones_por_tipo': funciones_por_tipo,
    })


def registro(request):
    if request.method == 'POST':
        formulario = UserCreationForm(request.POST)
        if formulario.is_valid():
            usuario = formulario.save()
            login(request, usuario)
            return redirect('listar_peliculas')
    else:
        formulario = UserCreationForm()

    return render(request, 'app/registro.html', {
        'formulario': formulario
    })


def login_usuario(request):
    if request.method == 'POST':
        formulario = AuthenticationForm(data=request.POST)
        if formulario.is_valid():
            usuario = formulario.get_user()
            login(request, usuario)
            return redirect('listar_peliculas')
    else:
        formulario = AuthenticationForm()

    return render(request, 'app/login.html', {
        'formulario': formulario
    })


def logout_usuario(request):
    logout(request)
    return redirect('listar_peliculas')




def seleccionar_butacas(request, funcion_id):
    funcion = Funcion.objects.get(id=funcion_id)
    butacas = Butaca.objects.filter(sala=funcion.sala).order_by('fila', 'numero')
    
    filas = {}
    for butaca in butacas:
        if butaca.fila not in filas:
            filas[butaca.fila] = []
        filas[butaca.fila].append(butaca)
    
    return render(request, 'app/butacas.html', {
        'funcion': funcion,
        'filas': filas,
    })

def confirmar_butacas(request, funcion_id):
    if request.method == 'POST':
        funcion = Funcion.objects.get(id=funcion_id)
        butacas_ids = request.POST.getlist('butacas')
        
        # Guardar en sesión para usarlos en confitería
        request.session['funcion_id'] = funcion_id
        request.session['butacas_ids'] = butacas_ids
        
        return redirect('confiteria')
    return redirect('listar_peliculas')


def confiteria(request):
    productos = ProductoConfiteria.objects.all()
    categorias = ProductoConfiteria.CATEGORIA_CHOICES
    return render(request, 'app/confiteria.html', {
        'productos': productos,
        'categorias': categorias,
    })


def pago(request):
    if request.method == 'POST':
        funcion_id = request.session.get('funcion_id')
        butacas_ids = request.session.get('butacas_ids', [])
        funcion = Funcion.objects.get(id=funcion_id)
        
        # Crear la compra
        compra = Compra.objects.create(
            usuario=request.user,
            funcion=funcion,
            total=funcion.precio * len(butacas_ids)
        )
        
        # Guardar entradas y marcar butacas como ocupadas
        for butaca_id in butacas_ids:
            butaca = Butaca.objects.get(id=butaca_id)
            butaca.estado = 'ocupada'
            butaca.save()
            Entrada.objects.create(compra=compra, butaca=butaca)
        
        # Guardar items de confitería
        for key, value in request.POST.items():
            if key.startswith('cantidad_') and int(value) > 0:
                producto_id = key.replace('cantidad_', '')
                producto = ProductoConfiteria.objects.get(id=producto_id)
                ItemConfiteria.objects.create(
                    compra=compra,
                    producto=producto,
                    cantidad=int(value)
                )
        
        return redirect('confirmacion', compra_id=compra.id)
    
    return redirect('listar_peliculas')


def confirmacion(request, compra_id):
    compra = Compra.objects.get(id=compra_id)
    entradas = Entrada.objects.filter(compra=compra)
    items = ItemConfiteria.objects.filter(compra=compra)
    return render(request, 'app/confirmacion_pago.html', {
        'compra': compra,
        'entradas': entradas,
        'items': items,
    })

@login_required
def perfil(request):
    try:
        perfil = request.user.perfilusuario
    except:
        perfil = None
    
    compras = Compra.objects.filter(usuario=request.user).order_by('-fecha_compra')
    
    return render(request, 'app/perfil.html', {
        'perfil': perfil,
        'compras': compras,
    })