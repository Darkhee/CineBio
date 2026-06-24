from functools import wraps
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.contrib import messages
from app.models import Pelicula, Funcion, ProductoConfiteria, Sala, Compra
from django.contrib.auth.models import User
from .forms import PeliculaAdminForm, FuncionAdminForm, ProductoAdminForm



def admin_requerido(vista):
    @wraps(vista)
    def wrapper(request, *args, **kwargs):
        if not request.session.get('portal_admin_uid'):
            return redirect('portal_admin:login')
        return vista(request, *args, **kwargs)
    return wrapper


def login_admin(request):  
    if request.session.get('portal_admin_uid'):
        return redirect('portal_admin:dashboard')

    error = None
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        usuario = authenticate(request, username=username, password=password)

        if usuario is not None and usuario.is_staff:
            request.session['portal_admin_uid']      = usuario.pk
            request.session['portal_admin_username'] = usuario.username
            return redirect('portal_admin:dashboard')
        else:
            error = 'Credenciales incorrectas o sin permisos de administrador.'

    return render(request, 'portal_admin/login.html', {'error': error})


def logout_admin(request):
    request.session.pop('portal_admin_uid', None)
    request.session.pop('portal_admin_username', None)
    return redirect('portal_admin:login')

@admin_requerido
def dashboard(request):
    contexto = {
        'total_peliculas': Pelicula.objects.count(),
        'total_funciones': Funcion.objects.count(),
        'total_productos': ProductoConfiteria.objects.count(),
        'total_salas': Sala.objects.count(),
        'total_compras': Compra.objects.count(),
        'ultimas_funciones': Funcion.objects.select_related('pelicula', 'sala').order_by('-fecha', '-hora')[:5],
        'ultimas_peliculas': Pelicula.objects.order_by('-id')[:4],
    }
    return render(request, 'portal_admin/dashboard.html', contexto)


@admin_requerido
def peliculas_list(request):
    peliculas = Pelicula.objects.all().order_by('nombre')
    return render(request, 'portal_admin/peliculas_list.html', {'peliculas': peliculas})


@admin_requerido
def pelicula_create(request):
    if request.method == 'POST':
        form = PeliculaAdminForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Película creada correctamente.')
            return redirect('portal_admin:peliculas_list')
    else:
        form = PeliculaAdminForm()
    return render(request, 'portal_admin/pelicula_form.html', {
        'form': form,
        'titulo': 'Nueva Película',
        'boton': 'Crear Película',
    })


@admin_requerido
def pelicula_edit(request, pk):
    pelicula = get_object_or_404(Pelicula, pk=pk)
    if request.method == 'POST':
        form = PeliculaAdminForm(request.POST, request.FILES, instance=pelicula)
        if form.is_valid():
            form.save()
            messages.success(request, f'Película "{pelicula.nombre}" actualizada.')
            return redirect('portal_admin:peliculas_list')
    else:
        form = PeliculaAdminForm(instance=pelicula)
    return render(request, 'portal_admin/pelicula_form.html', {
        'form': form,
        'pelicula': pelicula,
        'titulo': f'Editar: {pelicula.nombre}',
        'boton': 'Guardar Cambios',
    })

def _cancelar_funcion(funcion):  
    info = (
        f"{funcion.pelicula.nombre} — "
        f"{funcion.fecha.strftime('%d/%m/%Y')} {funcion.hora.strftime('%H:%M')} — "
        f"{funcion.sala.nombre}"
    )
    compras_afectadas = list(Compra.objects.filter(funcion=funcion, estado='completada'))
    for compra in compras_afectadas:
        compra.estado = 'pendiente_devolucion'
        compra.funcion_cancelada_info = info
        compra.save()
    return compras_afectadas



@admin_requerido
def pelicula_delete(request, pk):
    pelicula = get_object_or_404(Pelicula, pk=pk)
    if request.method == 'POST':
        nombre = pelicula.nombre
        funciones = Funcion.objects.filter(pelicula=pelicula)

        compras_afectadas = []
        for funcion in funciones:
            compras_afectadas += _cancelar_funcion(funcion)

        pelicula.delete()

        if compras_afectadas:
            monto_total = sum(c.total for c in compras_afectadas)
            messages.warning(
                request,
                f'Película "{nombre}" eliminada junto a sus funciones. '
                f'Se generaron {len(compras_afectadas)} devolución(es) pendiente(s) '
                f'por un total de ${monto_total:,.0f}. Se simuló el aviso por correo a cada cliente afectado.'
            )
        else:
            messages.success(request, f'Película "{nombre}" eliminada.')

        return redirect('portal_admin:peliculas_list')
    return render(request, 'portal_admin/confirmar_eliminar.html', {
        'objeto': pelicula.nombre,
        'tipo': 'película',
        'cancelar_url': 'portal_admin:peliculas_list',
    })


@admin_requerido
def funciones_list(request):
    funciones = Funcion.objects.select_related('pelicula', 'sala').order_by('-fecha', '-hora')
    return render(request, 'portal_admin/funciones_list.html', {'funciones': funciones})


@admin_requerido
def funcion_create(request):
    if request.method == 'POST':
        form = FuncionAdminForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Función creada correctamente.')
            return redirect('portal_admin:funciones_list')
    else:
        form = FuncionAdminForm()
    return render(request, 'portal_admin/funcion_form.html', {
        'form': form,
        'titulo': 'Nueva Función',
        'boton': 'Crear Función',
    })


@admin_requerido
def funcion_edit(request, pk):
    funcion = get_object_or_404(Funcion, pk=pk)
    if request.method == 'POST':
        form = FuncionAdminForm(request.POST, instance=funcion)
        if form.is_valid():
            form.save()
            messages.success(request, 'Función actualizada correctamente.')
            return redirect('portal_admin:funciones_list')
    else:
        form = FuncionAdminForm(instance=funcion)
    return render(request, 'portal_admin/funcion_form.html', {
        'form': form,
        'funcion': funcion,
        'titulo': f'Editar Función: {funcion.pelicula.nombre}',
        'boton': 'Guardar Cambios',
    })


@admin_requerido
def funcion_delete(request, pk):
    funcion = get_object_or_404(Funcion, pk=pk)
    if request.method == 'POST':
        descripcion = f'{funcion.pelicula.nombre} — {funcion.fecha} {funcion.hora}'
        compras_afectadas = _cancelar_funcion(funcion)
        funcion.delete()

        if compras_afectadas:
            monto_total = sum(c.total for c in compras_afectadas)
            messages.warning(
                request,
                f'Función "{descripcion}" eliminada. '
                f'Se generaron {len(compras_afectadas)} devolución(es) pendiente(s) '
                f'por un total de ${monto_total:,.0f}. Se simuló el aviso por correo a cada cliente afectado.'
            )
        else:
            messages.success(request, f'Función "{descripcion}" eliminada.')

        return redirect('portal_admin:funciones_list')
    return render(request, 'portal_admin/confirmar_eliminar.html', {
        'objeto': f'{funcion.pelicula.nombre} — {funcion.fecha} {funcion.hora}',
        'tipo': 'función',
        'cancelar_url': 'portal_admin:funciones_list',
    })

@admin_requerido
def productos_list(request):
    productos = ProductoConfiteria.objects.all().order_by('categoria', 'nombre')
    return render(request, 'portal_admin/productos_list.html', {'productos': productos})


@admin_requerido
def producto_create(request):
    if request.method == 'POST':
        form = ProductoAdminForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Producto creado correctamente.')
            return redirect('portal_admin:productos_list')
    else:
        form = ProductoAdminForm()
    return render(request, 'portal_admin/producto_form.html', {
        'form': form,
        'titulo': 'Nuevo Producto',
        'boton': 'Crear Producto',
    })


@admin_requerido
def producto_edit(request, pk):
    producto = get_object_or_404(ProductoConfiteria, pk=pk)
    if request.method == 'POST':
        form = ProductoAdminForm(request.POST, request.FILES, instance=producto)
        if form.is_valid():
            form.save()
            messages.success(request, f'Producto "{producto.nombre}" actualizado.')
            return redirect('portal_admin:productos_list')
    else:
        form = ProductoAdminForm(instance=producto)
    return render(request, 'portal_admin/producto_form.html', {
        'form': form,
        'producto': producto,
        'titulo': f'Editar: {producto.nombre}',
        'boton': 'Guardar Cambios',
    })


@admin_requerido
def producto_delete(request, pk):
    producto = get_object_or_404(ProductoConfiteria, pk=pk)
    if request.method == 'POST':
        nombre = producto.nombre
        producto.delete()
        messages.success(request, f'Producto "{nombre}" eliminado.')
        return redirect('portal_admin:productos_list')
    return render(request, 'portal_admin/confirmar_eliminar.html', {
        'objeto': producto.nombre,
        'tipo': 'producto',
        'cancelar_url': 'portal_admin:productos_list',
    })

@admin_requerido
def ventas_list(request):
    from app.models import Entrada, ItemConfiteria
    compras = (
        Compra.objects
        .select_related('usuario', 'funcion__pelicula', 'funcion__sala')
        .prefetch_related('entrada_set__butaca', 'itemconfiteria_set__producto')
        .order_by('-fecha_compra')
    )
    total_recaudado = sum(c.total for c in compras)
    return render(request, 'portal_admin/ventas_list.html', {
        'compras': compras,
        'total_recaudado': total_recaudado,
    })

@admin_requerido
def venta_detalle(request, compra_id):
    from app.models import Entrada, ItemConfiteria
    compra = get_object_or_404(
        Compra.objects.select_related('usuario', 'funcion__pelicula', 'funcion__sala')
        .prefetch_related('entrada_set__butaca', 'itemconfiteria_set__producto'),
        pk=compra_id
    )
    entradas = compra.entrada_set.all()
    items = compra.itemconfiteria_set.all()

    total_entradas = compra.funcion.precio * entradas.count() if compra.funcion else 0
    total_confiteria = sum(item.subtotal for item in items)

    perfil = None
    if compra.usuario:
        try:
            perfil = compra.usuario.perfilusuario
        except Exception:
            perfil = None

    return render(request, 'portal_admin/venta_detalle.html', {
        'compra': compra,
        'entradas': entradas,
        'items': items,
        'perfil': perfil,
        'total_entradas': total_entradas,
        'total_confiteria': total_confiteria,
    })

@admin_requerido
def procesar_devolucion(request, compra_id):
    compra = get_object_or_404(Compra, pk=compra_id)

    if request.method == 'POST' and compra.estado == 'pendiente_devolucion':
        from django.utils import timezone

        correo_simulado = (
            f"Para: {compra.correo_cliente}\n"
            f"Asunto: Cancelación de función y devolución de tu compra #{compra.id}\n\n"
            f"Hola {compra.nombre_cliente},\n\n"
            f"Lamentamos informarte que la función \"{compra.funcion_cancelada_info}\" "
            f"fue cancelada. Hemos procesado la devolución de tu compra por un monto de "
            f"${compra.total:,.0f}.\n\nGracias por tu comprensión.\nCineBio"
        )

        compra.estado = 'devuelta'
        compra.fecha_devolucion = timezone.now()
        compra.save()

        messages.success(
            request,
            f'Devolución de ${compra.total:,.0f} procesada para {compra.nombre_cliente}. '
            f'Se envió un correo de aviso con la siguiente información:\n\n{correo_simulado}'
        )

    return redirect('portal_admin:venta_detalle', compra_id=compra.id)

@admin_requerido
def usuarios_list(request):
    usuarios = (
        User.objects.filter(is_staff=False)
        .select_related('perfilusuario')
        .order_by('-date_joined')
    )
    return render(request, 'portal_admin/lista_usuarios.html', {'usuarios': usuarios})


@admin_requerido
def butacas_salas(request):
    from app.models import Sala
    salas = Sala.objects.all()
    return render(request, 'portal_admin/butacas_salas.html', {'salas': salas})


@admin_requerido
def butacas_sala_detalle(request, sala_id):
    from app.models import Sala, Butaca
    from collections import defaultdict
    sala = get_object_or_404(Sala, pk=sala_id)

    if request.method == 'POST':
        ids_inhabilitar = set(map(int, request.POST.getlist('butacas_inhabilitar')))
        todas = Butaca.objects.filter(sala=sala)
        for b in todas:
            b.estado = 'inhabilitada' if b.id in ids_inhabilitar else 'disponible'
            b.save()
        messages.success(request, f'Butacas de {sala.nombre} actualizadas.')
        return redirect('portal_admin:butacas_sala_detalle', sala_id=sala.pk)

    butacas = Butaca.objects.filter(sala=sala).order_by('fila', 'numero')
    filas = defaultdict(list)
    for b in butacas:
        filas[b.fila].append(b)

    return render(request, 'portal_admin/butacas_sala_detalle.html', {
        'sala': sala,
        'filas': dict(filas),
    })
