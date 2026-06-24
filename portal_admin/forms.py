from datetime import date, timedelta
from django import forms
from app.models import Pelicula, Funcion, ProductoConfiteria


class PeliculaAdminForm(forms.ModelForm):
    class Meta:
        model = Pelicula
        fields = ['nombre', 'imagen', 'descripcion', 'duracion']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'admin-input',
                'placeholder': 'Nombre de la película',
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'admin-input',
                'rows': 4,
                'placeholder': 'Descripción de la película',
            }),
            'duracion': forms.NumberInput(attrs={
                'class': 'admin-input',
                'placeholder': 'Duración en minutos',
                'min': 1,
            }),
            'imagen': forms.ClearableFileInput(attrs={
                'class': 'admin-file-input',
            }),
        }
        labels = {
            'nombre': 'Nombre',
            'imagen': 'Póster / Imagen',
            'descripcion': 'Descripción',
            'duracion': 'Duración (minutos)',
        }


class FuncionAdminForm(forms.ModelForm):
    class Meta:
        model = Funcion
        fields = ['pelicula', 'sala', 'fecha', 'hora', 'precio', 'tipo']
        widgets = {
            'pelicula': forms.Select(attrs={'class': 'admin-input'}),
            'sala': forms.Select(attrs={'class': 'admin-input'}),
            'fecha': forms.DateInput(attrs={
                'class': 'admin-input',
                'type': 'date',
            }),
            'hora': forms.TimeInput(attrs={
                'class': 'admin-input',
                'type': 'time',
            }),
            'precio': forms.NumberInput(attrs={
                'class': 'admin-input',
                'placeholder': 'Precio en CLP',
                'min': 0,
                'max': 200000,
            }),
            'tipo': forms.Select(attrs={'class': 'admin-input'}),
        }
        labels = {
            'pelicula': 'Película',
            'sala': 'Sala',
            'fecha': 'Fecha',
            'hora': 'Hora',
            'precio': 'Precio (CLP)',
            'tipo': 'Tipo de función',
        }
        

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        hoy = date.today()
        limite = hoy + timedelta(days=7)
        self.fields['fecha'].widget.attrs['min'] = hoy.isoformat()
        self.fields['fecha'].widget.attrs['max'] = limite.isoformat()
        self.fields['fecha'].help_text = (
            f'Solo puedes agendar funciones entre {hoy.strftime("%d/%m/%Y")} '
            f'y {limite.strftime("%d/%m/%Y")}.'
        )

    def clean_fecha(self):
        fecha = self.cleaned_data.get('fecha')
        hoy = date.today()
        limite = hoy + timedelta(days=7)
        if fecha < hoy:
            raise forms.ValidationError('No puedes agendar funciones en fechas pasadas.')
        if fecha > limite:
            raise forms.ValidationError(
                f'Solo puedes agendar funciones hasta el {limite.strftime("%d/%m/%Y")}.'
            )
        return fecha
    
    def clean_precio(self):
        precio = self.cleaned_data.get('precio')
        if precio is not None and precio > 200000:
            raise forms.ValidationError('El precio no puede superar los $200.000.')
        if precio is not None and precio < 0:
            raise forms.ValidationError('El precio no puede ser negativo.')
        return precio


class ProductoAdminForm(forms.ModelForm):
    class Meta:
        model = ProductoConfiteria
        fields = ['nombre', 'categoria', 'precio', 'stock', 'imagen']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'admin-input',
                'placeholder': 'Nombre del producto',
            }),
            'categoria': forms.Select(attrs={'class': 'admin-input'}),
            'precio': forms.NumberInput(attrs={
                'class': 'admin-input',
                'placeholder': 'Precio en CLP',
                'min': 0,
            }),
            'stock': forms.NumberInput(attrs={
                'class': 'admin-input',
                'placeholder': 'Cantidad disponible',
                'min': 0,
            }),
            'imagen': forms.ClearableFileInput(attrs={
                'class': 'admin-file-input',
            }),
        }
        labels = {
            'nombre': 'Nombre',
            'categoria': 'Categoría',
            'precio': 'Precio (CLP)',
            'stock': 'Stock disponible',
            'imagen': 'Imagen del producto',
        }