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


class ProductoAdminForm(forms.ModelForm):
    class Meta:
        model = ProductoConfiteria
        fields = ['nombre', 'categoria', 'precio', 'imagen']
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
            'imagen': forms.ClearableFileInput(attrs={
                'class': 'admin-file-input',
            }),
        }
        labels = {
            'nombre': 'Nombre',
            'categoria': 'Categoría',
            'precio': 'Precio (CLP)',
            'imagen': 'Imagen del producto',
        }
