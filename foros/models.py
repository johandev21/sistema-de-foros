from django.db import models
from django.utils import timezone

class Usuario(models.Model):
    TIPO_USUARIO = (
        ('Admin', 'Administrador'),
        ('Normal', 'Usuario Normal'),
    )

    ESTADO_CUENTA = (
        ('Activo', 'Activo'),
        ('Suspendido', 'Suspendido'),
        ('Deshabilitado', 'Deshabilitado'),
    )

    rut = models.CharField(max_length=12, unique=True)
    nombres = models.CharField(max_length=100)
    paterno = models.CharField(max_length=50)
    materno = models.CharField(max_length=50, null=True, blank=True)
    correo = models.EmailField(unique=True)
    nacionalidad = models.CharField(max_length=50)
    contrasena = models.CharField(max_length=128)
    tipo_usuario = models.CharField(max_length=10, choices=TIPO_USUARIO, default='Normal')
    estado = models.CharField(max_length=15, choices=ESTADO_CUENTA, default='Activo')
    intentos_fallidos = models.IntegerField(default=0)
    fecha_creacion = models.DateTimeField(default=timezone.now)
    foto = models.ImageField(upload_to='fotos_perfil/', null=True, blank=True)

    def __str__(self):
        return f"{self.nombres} {self.paterno} ({self.tipo_usuario}) - {self.estado}"

class Tematica(models.Model):
    nombre = models.CharField(max_length=50, unique=True)
    descripcion = models.TextField()

    def __str__(self):
        return self.nombre

class Foro(models.Model):
    nombre = models.CharField(max_length=30, unique=True)
    descripcion = models.TextField()
    imagen = models.ImageField(upload_to='foros/', null=True, blank=True)
    tematica = models.ForeignKey(Tematica, on_delete=models.CASCADE)
    fecha_creacion = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.nombre} - {self.tematica.nombre}"

class Publicacion(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    foro = models.ForeignKey(Foro, on_delete=models.CASCADE)
    titulo = models.CharField(max_length=120)
    texto = models.TextField()
    fecha = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Publicación de {self.usuario.nombres} en {self.foro.nombre} - {self.titulo}"

class Respuesta(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    publicacion = models.ForeignKey(Publicacion, on_delete=models.CASCADE)
    texto = models.TextField()
    fecha = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Respuesta de {self.usuario.nombres} a {self.publicacion.titulo}"

class Historial(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    accion = models.TextField()
    fecha = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.usuario.nombres} - {self.accion} ({self.fecha.strftime('%Y-%m-%d %H:%M:%S')})"

class Palabrotas(models.Model):
    palabra = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.palabra
