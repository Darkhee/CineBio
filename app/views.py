from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from .models import (
    Pelicula, Funcion, Butaca, ProductoConfiteria,
    Compra, Entrada, ItemConfiteria, PerfilUsuario
)


# ──────────────────────────────────────────────────────────────
# Películas
# ──────────────────────────────────────────────────────────────

def listar_peliculas(request):
    peliculas = Pelicula.objects.all()
    return render(request, 'app/listar_peliculas.html', {'peliculas': peliculas})


def detalle_pelicula(request, id):
    pelicula = get_object_or_404(Pelicula, id=id)
    funciones = Funcion.objects.filter(pelicula=pelicula)

    funciones_por_tipo = {}
    for funcion in funciones:
        tipo = funcion.get_tipo_display()
        funciones_por_tipo.setdefault(tipo, []).append(funcion)

    return render(request, 'app/detalle_pelicula.html', {
        'pelicula': pelicula,
        'funciones_por_tipo': funciones_por_tipo,
    })


# ──────────────────────────────────────────────────────────────
# Autenticación
# ──────────────────────────────────────────────────────────────

def registro(request):
    from .forms import SocioRegistroForm
    from django.contrib.auth.models import User

    errores = {}

    if request.method == 'POST':
        form = SocioRegistroForm(request.POST)
        if form.is_valid():
            d = form.cleaned_data
            if d['contrasena'] != d['confirmar_contrasena']:
                errores['confirmar_contrasena'] = 'Las contraseñas no coinciden.'
            elif User.objects.filter(username=d['correo']).exists():
                errores['correo'] = 'Ya existe una cuenta con ese correo.'
            else:
                usuario = User.objects.create_user(
                    username=d['correo'],
                    email=d['correo'],
                    password=d['contrasena'],
                    first_name=d['nombre'],
                    last_name=d['apellido_paterno'],
                )
                PerfilUsuario.objects.create(
                    usuario=usuario,
                    tipo_documento=d['tipo_documento'],
                    rut=d['rut'],
                    nombre=d['nombre'],
                    apellido_paterno=d['apellido_paterno'],
                    apellido_materno=d['apellido_materno'],
                    genero=d['genero'],
                    fecha_nacimiento=d['fecha_nacimiento'],
                    telefono=d['celular'],
                    region=d['region'],
                    provincia=d['provincia'],
                    comuna=d['comuna'],
                )
                login(request, usuario)
                return redirect('listar_peliculas')
        for field, error_list in form.errors.items():
            if field not in errores:
                errores[field] = error_list[0]
    else:
        form = SocioRegistroForm()

    return render(request, 'app/registro.html', {'formulario': form, 'errores': errores})


def login_usuario(request):
    next_url = request.GET.get('next', '')
    if request.method == 'POST':
        formulario = AuthenticationForm(data=request.POST)
        if formulario.is_valid():
            usuario = formulario.get_user()
            login(request, usuario)
            # Si viene del flujo de compra, continuar a confitería
            next_page = request.POST.get('next', '')
            if next_page:
                return redirect(next_page)
            return redirect('listar_peliculas')
    else:
        formulario = AuthenticationForm()

    return render(request, 'app/login.html', {
        'formulario': formulario,
        'next': next_url,
    })


def logout_usuario(request):
    logout(request)
    return redirect('listar_peliculas')


# ──────────────────────────────────────────────────────────────
# Butacas: lógica por función
# ──────────────────────────────────────────────────────────────

def seleccionar_butacas(request, funcion_id):
    funcion = get_object_or_404(Funcion, id=funcion_id)

    # IDs de butacas ocupadas EN ESTA FUNCIÓN (no de forma global)
    ocupadas_esta_funcion = set(
        Entrada.objects.filter(compra__funcion=funcion)
        .values_list('butaca_id', flat=True)
    )

    butacas_qs = Butaca.objects.filter(sala=funcion.sala).order_by('fila', 'numero')

    # Calcular estado_vista por butaca (no toca el estado global del modelo)
    for b in butacas_qs:
        if b.estado == 'inhabilitada':
            b.estado_vista = 'inhabilitada'
        elif b.id in ocupadas_esta_funcion:
            b.estado_vista = 'ocupada'
        else:
            b.estado_vista = 'disponible'

    filas = {}
    for b in butacas_qs:
        filas.setdefault(b.fila, []).append(b)

    return render(request, 'app/butacas.html', {'funcion': funcion, 'filas': filas})


def confirmar_butacas(request, funcion_id):
    if request.method == 'POST':
        butacas_ids = request.POST.getlist('butacas')
        request.session['funcion_id'] = funcion_id
        request.session['butacas_ids'] = butacas_ids
        request.session.pop('invitado', None)   # limpiar invitado anterior si lo hay

        # Si ya está logueado como usuario normal, saltar directo a confitería
        if request.user.is_authenticated and not request.user.is_staff:
            return redirect('confiteria')

        return redirect('tipo_compra')
    return redirect('listar_peliculas')


# ──────────────────────────────────────────────────────────────
# Flujo de tipo de compra (registrado vs invitado)
# ──────────────────────────────────────────────────────────────

def tipo_compra(request):
    funcion_id       = request.session.get('funcion_id')
    butacas_ids      = request.session.get('butacas_ids', [])
    confiteria_items = request.session.get('confiteria_items', {})

    if not butacas_ids and not confiteria_items:
        return redirect('listar_peliculas')

    funcion = None
    if funcion_id:
        funcion = get_object_or_404(Funcion, id=funcion_id)

    return render(request, 'app/tipo_compra.html', {
        'funcion': funcion,
        'cantidad_butacas': len(butacas_ids),
        'tiene_items': bool(confiteria_items),
    })

def datos_invitado(request):
    confiteria_items = request.session.get('confiteria_items', {})
    butacas_ids      = request.session.get('butacas_ids', [])
    if not butacas_ids and not confiteria_items:
        return redirect('listar_peliculas')

    errores = {}
    if request.method == 'POST':
        tipo_doc  = request.POST.get('tipo_doc', '').strip()
        documento = request.POST.get('documento', '').strip()
        nombre    = request.POST.get('nombre', '').strip()
        apellido  = request.POST.get('apellido', '').strip()
        correo    = request.POST.get('correo', '').strip()

        if not tipo_doc:   errores['tipo_doc']  = 'Selecciona el tipo de documento.'
        if not documento:  errores['documento'] = 'Ingresa tu número de documento.'
        if not nombre:     errores['nombre']    = 'Ingresa tu nombre.'
        if not apellido:   errores['apellido']  = 'Ingresa tu apellido.'
        if not correo:     errores['correo']    = 'Ingresa tu correo.'

        if not errores:
            request.session['invitado'] = {
                'tipo_doc':  tipo_doc,
                'documento': documento,
                'nombre':    nombre,
                'apellido':  apellido,
                'correo':    correo,
            }
            if request.session.get('confiteria_items'):
                return redirect('pago')
            return redirect('confiteria')

    return render(request, 'app/datos_invitado.html', {'errores': errores})


# ──────────────────────────────────────────────────────────────
# Confitería
# ──────────────────────────────────────────────────────────────
def confiteria(request):
    if request.method == 'POST':
        items = {}
        for key, value in request.POST.items():
            if key.startswith('cantidad_') and value.isdigit() and int(value) > 0:
                items[key] = value
        request.session['confiteria_items'] = items

        if not items:
            return redirect('confiteria')

        usuario_ok = request.user.is_authenticated and not request.user.is_staff
        if usuario_ok or request.session.get('invitado'):
            return redirect('pago')

        return redirect('tipo_compra')

    productos  = ProductoConfiteria.objects.all()
    categorias = ProductoConfiteria.CATEGORIA_CHOICES
    return render(request, 'app/confiteria.html', {
        'productos': productos,
        'categorias': categorias,
    })


# ──────────────────────────────────────────────────────────────
# Pago: soporta usuario registrado e invitado, y suma confitería
# ──────────────────────────────────────────────────────────────

def pago(request):
    funcion_id       = request.session.get('funcion_id')
    butacas_ids      = request.session.get('butacas_ids', [])
    invitado         = request.session.get('invitado')
    confiteria_items = request.session.get('confiteria_items', {})

    if not butacas_ids and not confiteria_items:
        return redirect('listar_peliculas')

    usuario_ok = request.user.is_authenticated and not request.user.is_staff
    if not usuario_ok and not invitado:
        return redirect('tipo_compra')

    funcion = get_object_or_404(Funcion, id=funcion_id) if funcion_id else None

    total_entradas = funcion.precio * len(butacas_ids) if funcion and butacas_ids else 0

    total_confiteria = 0
    items_compra = []
    for key, value in confiteria_items.items():
        pid = key.replace('cantidad_', '')
        try:
            producto = ProductoConfiteria.objects.get(id=pid)
            cantidad = int(value)
            total_confiteria += producto.precio * cantidad
            items_compra.append((producto, cantidad))
        except ProductoConfiteria.DoesNotExist:
            pass

    total = total_entradas + total_confiteria

    if usuario_ok:
        compra = Compra.objects.create(
            usuario=request.user,
            funcion=funcion,
            total=total,
        )
    else:
        compra = Compra.objects.create(
            usuario=None,
            funcion=funcion,
            total=total,
            inv_tipo_doc  = invitado.get('tipo_doc', ''),
            inv_documento = invitado.get('documento', ''),
            inv_nombre    = invitado.get('nombre', ''),
            inv_apellido  = invitado.get('apellido', ''),
            inv_correo    = invitado.get('correo', ''),
        )

    for bid in butacas_ids:
        butaca = get_object_or_404(Butaca, id=bid)
        Entrada.objects.create(compra=compra, butaca=butaca)

    for producto, cantidad in items_compra:
        ItemConfiteria.objects.create(compra=compra, producto=producto, cantidad=cantidad)

    # Puntos y visitas para socios registrados
    if usuario_ok:
        try:
            perfil = request.user.perfilusuario
            if butacas_ids:
                perfil.visitas += 1   # visita solo si compró entradas
            if total >= 2000:
                perfil.puntos += total // 2000  # puntos por cualquier compra
            perfil.save()
        except Exception:
            pass

    for key in ('funcion_id', 'butacas_ids', 'invitado', 'confiteria_items'):
        request.session.pop(key, None)

    return redirect('metodo_pago', compra_id=compra.id)


def metodo_pago(request, compra_id):
    compra = get_object_or_404(Compra, id=compra_id)
    error = None

    if request.method == 'POST':
        metodo = request.POST.get('metodo')
        if not metodo:
            error = 'Debes seleccionar un método de pago.'
        else:
            return redirect('confirmacion', compra_id=compra.id)

    entradas = Entrada.objects.filter(compra=compra)
    items    = ItemConfiteria.objects.filter(compra=compra)
    return render(request, 'app/metodo_pago.html', {
        'compra':   compra,
        'entradas': entradas,
        'items':    items,
        'error':    error,
    })

def confirmacion(request, compra_id):
    compra  = get_object_or_404(Compra, id=compra_id)
    entradas = Entrada.objects.filter(compra=compra)
    items    = ItemConfiteria.objects.filter(compra=compra)
    return render(request, 'app/confirmacion_pago.html', {
        'compra':   compra,
        'entradas': entradas,
        'items':    items,
    })


@login_required
def perfil(request):
    try:
        perfil = request.user.perfilusuario
    except Exception:
        perfil = None
    compras = Compra.objects.filter(usuario=request.user).order_by('-fecha_compra')
    return render(request, 'app/perfil.html', {'perfil': perfil, 'compras': compras})
