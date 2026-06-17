from django.contrib import admin
from django import forms
from .models import (
    Pelicula, Sala, Funcion, Butaca,
    ProductoConfiteria, Compra, Entrada, ItemConfiteria, PerfilUsuario
)

# ─────────────────────────────────────────────
# Django Admin: SÓLO Salas y Butacas
# El resto (Películas, Funciones, Productos) se
# gestiona desde el Portal de Administración en /gestion/
# ─────────────────────────────────────────────

class SalaAdminForm(forms.ModelForm):
    configuracion = forms.JSONField(
        help_text='Ejemplo: {"A": 8, "B": 8, "C": 8, "D": 8, "E": 8}'
    )

    class Meta:
        model = Sala
        fields = '__all__'


class SalaAdmin(admin.ModelAdmin):
    form = SalaAdminForm
    list_display = ('nombre',)


class ButacaAdmin(admin.ModelAdmin):
    list_display = ('sala', 'fila', 'numero', 'estado')
    list_filter = ('sala', 'estado')


# Modelos registrados en el Django Admin
admin.site.register(Sala, SalaAdmin)
admin.site.register(Butaca, ButacaAdmin)

# Los demás modelos se administran en /gestion/ y NO aparecen en /admin/
# admin.site.register(Pelicula)      ← gestionado en portal_admin
# admin.site.register(Funcion)       ← gestionado en portal_admin
# admin.site.register(ProductoConfiteria) ← gestionado en portal_admin

# Modelos de sólo lectura / referencia (pueden quedar visibles para auditoría)
admin.site.register(Compra)
admin.site.register(Entrada)
admin.site.register(ItemConfiteria)
admin.site.register(PerfilUsuario)