from django.contrib import admin
from django import forms
from .models import (
    Pelicula, Sala, Funcion, Butaca,
    ProductoConfiteria, Compra, Entrada, ItemConfiteria, PerfilUsuario
)

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


admin.site.register(Sala, SalaAdmin)
admin.site.register(Butaca, ButacaAdmin)
admin.site.register(Compra)
admin.site.register(Entrada)
admin.site.register(ItemConfiteria)
admin.site.register(PerfilUsuario)