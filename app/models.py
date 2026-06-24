from django.db import models
from django.contrib.auth.models import User

class PerfilUsuario(models.Model):
    CATEGORIA_CHOICES = [
        ('clasico', 'CineBio Clásico'),
        ('plata', 'CineBio Plata'),
        ('oro', 'CineBio Oro'),
        ('black', 'CineBio Black'),
    ]
    TIPO_DOC_CHOICES = [
        ('RUT', 'RUT'),
        ('PASAPORTE', 'Pasaporte'),
    ]
    GENERO_CHOICES = [
        ('M', 'Masculino'),
        ('F', 'Femenino'),
    ]

    INFO_CATEGORIAS = {
        'clasico': {
            'nombre': 'CineBio Clásico',
            'visitas_minimas': 0,
            'beneficios': [
                'Acumulación de puntos en cada compra',
                'Acceso a promociones generales',
            ],
        },
        'plata': {
            'nombre': 'CineBio Plata',
            'visitas_minimas': 6,
            'beneficios': [
                'Todo lo de Clásico',
                '5% de descuento en confitería',
                'Acceso prioritario a preventas',
            ],
        },
        'oro': {
            'nombre': 'CineBio Oro',
            'visitas_minimas': 10,
            'beneficios': [
                'Todo lo de Plata',
                '10% de descuento en entradas',
                'Combo de cumpleaños gratis',
            ],
        },
        'black': {
            'nombre': 'CineBio Black',
            'visitas_minimas': 15,
            'beneficios': [
                'Todo lo de Oro',
                '15% de descuento en entradas y confitería',
                'Invitaciones a preestrenos exclusivos',
                'Atención preferencial en boletería',
            ],
        },
    }

    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    # Documento
    tipo_documento = models.CharField(max_length=20, choices=TIPO_DOC_CHOICES, default='RUT')
    rut = models.CharField(max_length=20, verbose_name='Número de documento')
    # Datos personales
    nombre = models.CharField(max_length=100, blank=True)
    apellido_paterno = models.CharField(max_length=100, blank=True)
    apellido_materno = models.CharField(max_length=100, blank=True)
    genero = models.CharField(max_length=1, choices=GENERO_CHOICES, blank=True)
    fecha_nacimiento = models.DateField(null=True, blank=True)
    # Contacto
    telefono = models.CharField(max_length=15, blank=True)
    # Ubicacion
    region = models.CharField(max_length=100, blank=True)
    provincia = models.CharField(max_length=100, blank=True)
    comuna = models.CharField(max_length=100, blank=True)
    # Club
    visitas = models.IntegerField(default=0)
    puntos = models.FloatField(default=0)
    categoria = models.CharField(max_length=20, choices=CATEGORIA_CHOICES, default='clasico')

    def __str__(self):
        return f"Perfil de {self.usuario.username}"

    def nombre_completo(self):
        return f"{self.nombre} {self.apellido_paterno} {self.apellido_materno}".strip()

    def actualizar_categoria(self):
        """Recalcula la categoría según las visitas acumuladas. No guarda por sí sola."""
        if self.visitas >= 15:
            nueva = 'black'
        elif self.visitas >= 10:
            nueva = 'oro'
        elif self.visitas >= 6:
            nueva = 'plata'
        else:
            nueva = 'clasico'
        self.categoria = nueva
        return nueva

    def visitas_para_siguiente(self):
        """Devuelve (visitas_faltantes, nombre_siguiente_categoria) o (0, None) si ya es Black."""
        if self.visitas < 6:
            return 6 - self.visitas, self.INFO_CATEGORIAS['plata']['nombre']
        elif self.visitas < 10:
            return 10 - self.visitas, self.INFO_CATEGORIAS['oro']['nombre']
        elif self.visitas < 15:
            return 15 - self.visitas, self.INFO_CATEGORIAS['black']['nombre']
        else:
            return 0, None


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
        ('3d_doblada', '3D Doblada'),
        ('3d_subtitulada', '3D Subtitulada'),
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
    stock = models.IntegerField(default=0)
    imagen = models.ImageField(upload_to='confiteria/')

    def __str__(self):
        return self.nombre


class Compra(models.Model):
    ESTADO_CHOICES = [
        ('completada', 'Completada'),
        ('pendiente_devolucion', 'Pendiente de Devolución'),
        ('devuelta', 'Devuelta'),
    ]

    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    funcion = models.ForeignKey(Funcion, on_delete=models.SET_NULL, null=True, blank=True)
    fecha_compra = models.DateTimeField(auto_now_add=True)
    total = models.IntegerField(default=0)

    inv_tipo_doc  = models.CharField(max_length=20, blank=True, default='')
    inv_documento = models.CharField(max_length=20, blank=True, default='')
    inv_nombre    = models.CharField(max_length=100, blank=True, default='')
    inv_apellido  = models.CharField(max_length=100, blank=True, default='')
    inv_correo    = models.EmailField(blank=True, default='')

    estado = models.CharField(max_length=30, choices=ESTADO_CHOICES, default='completada')
    funcion_cancelada_info = models.CharField(max_length=255, blank=True, default='')
    fecha_devolucion = models.DateTimeField(null=True, blank=True)

    @property
    def es_invitado(self):
        return self.usuario is None

    @property
    def correo_cliente(self):
        if self.usuario:
            return self.usuario.email
        return self.inv_correo

    @property
    def nombre_cliente(self):
        if self.usuario:
            return self.usuario.get_full_name() or self.usuario.username
        return f"{self.inv_nombre} {self.inv_apellido}".strip()

    def __str__(self):
        if self.usuario:
            return f"Compra {self.id} - {self.usuario}"
        return f"Compra {self.id} - Invitado ({self.inv_nombre})"

class Entrada(models.Model):
    compra = models.ForeignKey(Compra, on_delete=models.CASCADE)
    butaca = models.ForeignKey(Butaca, on_delete=models.CASCADE)

    def __str__(self):
        return f"Entrada {self.butaca}"


class ItemConfiteria(models.Model):
    compra = models.ForeignKey(Compra, on_delete=models.CASCADE)
    producto = models.ForeignKey(ProductoConfiteria, on_delete=models.CASCADE)
    cantidad = models.IntegerField(default=1)

    @property
    def subtotal(self):
        return self.producto.precio * self.cantidad

    def __str__(self):
        return f"{self.producto.nombre} x{self.cantidad}"