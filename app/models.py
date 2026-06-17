from django.db import models
from django.contrib.auth.models import User

class PerfilUsuario(models.Model):
    CATEGORIA_CHOICES = [
        ('estandar', 'SOCIO BIO-Estandar'),
        ('silver', 'SOCIO BIO-Silver'),
        ('gold', 'SOCIO BIO-Gold'),
    ]
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    rut = models.CharField(max_length=12)
    telefono = models.CharField(max_length=15, blank=True)
    visitas = models.IntegerField(default=0)
    puntos = models.FloatField(default=0)
    categoria = models.CharField(max_length=20, choices=CATEGORIA_CHOICES, default='estandar')

    def __str__(self):
        return f"Perfil de {self.usuario.username}"


class Pelicula(models.Model):
    nombre = models.CharField(max_length=200)
    imagen = models.ImageField(upload_to='peliculas/')
    descripcion = models.TextField()
    duracion = models.IntegerField()

    def __str__(self):
        return self.nombre


class Sala(models.Model):
    nombre = models.CharField(max_length=50)
    configuracion = models.JSONField(default=dict)
   

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if not Butaca.objects.filter(sala=self).exists():
            for fila, columnas in self.configuracion.items():
                for numero in range(1, columnas + 1):
                    Butaca.objects.create(
                        sala=self,
                        fila=fila,
                        numero=numero,
                        estado='disponible'
                    )

    def __str__(self):
        return self.nombre


class Funcion(models.Model):
    TIPO_CHOICES = [
        ('2d_doblada', '2D Doblada'),
        ('2d_subtitulada', '2D Subtitulada'),
        ('3d', '3D'),
    ]
    pelicula = models.ForeignKey(Pelicula, on_delete=models.CASCADE)
    sala = models.ForeignKey(Sala, on_delete=models.CASCADE)
    fecha = models.DateField()
    hora = models.TimeField()
    precio = models.IntegerField()
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, default='2d_doblada')

    def __str__(self):
        return f"{self.pelicula.nombre} - {self.fecha} {self.hora}"


class Butaca(models.Model):
    ESTADO_CHOICES = [
        ('disponible', 'Disponible'),
        ('ocupada', 'Ocupada'),
        ('inhabilitada', 'Inhabilitada'),
    ]
    sala = models.ForeignKey(Sala, on_delete=models.CASCADE)
    fila = models.CharField(max_length=5)
    numero = models.IntegerField()
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='disponible')

    def __str__(self):
        return f"{self.fila}{self.numero}"


class ProductoConfiteria(models.Model):
    CATEGORIA_CHOICES = [
        ('combo', 'Combo'),
        ('palomitas', 'Palomitas'),
        ('bebidas', 'Bebidas'),
        ('dulces', 'Dulces y Snacks'),
    ]
    nombre = models.CharField(max_length=100)
    categoria = models.CharField(max_length=20, choices=CATEGORIA_CHOICES)
    precio = models.IntegerField()
    imagen = models.ImageField(upload_to='confiteria/')

    def __str__(self):
        return self.nombre


class Compra(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    funcion = models.ForeignKey(Funcion, on_delete=models.CASCADE)
    fecha_compra = models.DateTimeField(auto_now_add=True)
    total = models.IntegerField(default=0)

    def __str__(self):
        return f"Compra {self.id} - {self.usuario}"


class Entrada(models.Model):
    compra = models.ForeignKey(Compra, on_delete=models.CASCADE)
    butaca = models.ForeignKey(Butaca, on_delete=models.CASCADE)

    def __str__(self):
        return f"Entrada {self.butaca}"


class ItemConfiteria(models.Model):
    compra = models.ForeignKey(Compra, on_delete=models.CASCADE)
    producto = models.ForeignKey(ProductoConfiteria, on_delete=models.CASCADE)
    cantidad = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.producto.nombre} x{self.cantidad}"