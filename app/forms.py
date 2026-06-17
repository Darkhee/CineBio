from django import forms
from .models import Pelicula

class PeliculaForm(forms.ModelForm):
    class Meta:
        model = Pelicula
        fields = ['nombre', 'imagen', 'descripcion', 'duracion']

# --- NUEVO FORMULARIO DE REGISTRO ---
class SocioRegistroForm(forms.Form):
    TIPO_DOC_CHOICES = [
        ('', 'Tipo de documento'),
        ('RUT', 'RUT'),
        ('PASAPORTE', 'Pasaporte'),
    ]
    GENERO_CHOICES = [
        ('M', 'Masculino'),
        ('F', 'Femenino'),
    ]

    # Columna Izquierda
    tipo_documento = forms.ChoiceField(choices=TIPO_DOC_CHOICES, widget=forms.Select(attrs={'class': 'form-input'}))
    correo = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-input', 'placeholder': 'Correo electrónico'}))
    apellido_paterno = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Apellido Paterno'}))
    contrasena = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-input', 'placeholder': 'Contraseña'}))
    fecha_nacimiento = forms.DateField(widget=forms.DateInput(attrs={'class': 'form-input', 'type': 'date', 'placeholder': 'Fecha de nacimiento'}))
    region = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Región'}))
    comuna = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Comuna'}))

    # Columna Derecha
    rut = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Número de RUT'}))
    nombre = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Nombre'}))
    apellido_materno = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Apellido Materno'}))
    confirmar_contrasena = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-input', 'placeholder': 'Confirmar contraseña'}))
    celular = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Número de celular'}))
    provincia = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Provincia'}))
    genero = forms.ChoiceField(choices=GENERO_CHOICES, widget=forms.RadioSelect(attrs={'class': 'form-radio'}))
    
    acepto_terminos = forms.BooleanField(required=True)