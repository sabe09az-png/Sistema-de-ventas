from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

# ========== MODELOS ORIGINALES ==========
class Coleccion(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    imagen = models.ImageField(upload_to='colecciones/', blank=True, null=True)
    def __str__(self):
        return self.nombre

class Categoria(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    imagen = models.ImageField(upload_to='categorias/', blank=True, null=True)
    def __str__(self):
        return self.nombre

class Juego(models.Model):
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField()
    precio = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    descargas = models.PositiveIntegerField(default=0)
    genero = models.CharField(max_length=100, default="Accion")
    idiomas = models.CharField(max_length=200, null=True, blank=True)
    desarrollador = models.CharField(max_length=200, blank=True, null=True)
    fecha_de_lanzamiento = models.DateField(default="2025-01-01")
    tamaño = models.CharField(max_length=50, null=True, blank=True)
    portada = models.ImageField(upload_to='portadas/', null=True, blank=True)
    archivo_juego = models.FileField(upload_to='juegos/', null=True, blank=True)
    coleccion = models.ForeignKey(Coleccion, on_delete=models.SET_NULL, null=True, blank=True)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, null=True, blank=True)
    def __str__(self):
        return self.titulo

class Carrito(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    def total(self):
        return sum(item.subtotal() for item in self.items.all())
    def __str__(self):
        return f"Carrito de {self.usuario.username}"

class CarritoItem(models.Model):
    carrito = models.ForeignKey(Carrito, related_name='items', on_delete=models.CASCADE)
    juego = models.ForeignKey(Juego, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(default=1)
    def subtotal(self):
        return self.juego.precio * self.cantidad
    def __str__(self):
        return f"{self.cantidad} x {self.juego.titulo}"

class Orden(models.Model):
    ESTADOS = [
        ('pendiente', 'Pendiente'),
        ('completada', 'Completada'),
        ('cancelada', 'Cancelada'),
    ]
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='pendiente')
    paypal_id = models.CharField(max_length=100, blank=True)
    def __str__(self):
        return f"Orden #{self.id} - {self.usuario.username}"

class OrdenItem(models.Model):
    orden = models.ForeignKey(Orden, related_name='items', on_delete=models.CASCADE)
    juego = models.ForeignKey(Juego, on_delete=models.CASCADE)
    precio = models.DecimalField(max_digits=8, decimal_places=2)
    cantidad = models.PositiveIntegerField(default=1)
    def subtotal(self):
        return self.precio * self.cantidad

class BibliotecaJuego(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    juego = models.ForeignKey(Juego, on_delete=models.CASCADE)
    fecha_compra = models.DateTimeField(auto_now_add=True)
    orden = models.ForeignKey(Orden, on_delete=models.CASCADE)
    def __str__(self):
        return f"{self.juego.titulo} - {self.usuario.username}"

# Señal para crear carrito al crear usuario
@receiver(post_save, sender=User)
def crear_carrito_usuario(sender, instance, created, **kwargs):
    if created:
        Carrito.objects.get_or_create(usuario=instance)

# Señal para incrementar descargas
@receiver(post_save, sender=BibliotecaJuego)
def incrementar_descargas(sender, instance, created, **kwargs):
    if created:
        instance.juego.descargas += 1
        instance.juego.save()

# ========== NUEVOS MODELOS DE INVENTARIO ==========
class Producto(models.Model):
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)
    precio_compra = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    precio_venta = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    stock = models.PositiveIntegerField(default=0)
    imagen = models.ImageField(upload_to='productos/', null=True, blank=True)
    def __str__(self):
        return f"{self.nombre} (Stock: {self.stock})"

class Proveedor(models.Model):
    nombre = models.CharField(max_length=200, unique=True)
    contacto = models.CharField(max_length=200, blank=True, null=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    direccion = models.TextField(blank=True, null=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.nombre

class Compra(models.Model):
    proveedor = models.ForeignKey(Proveedor, on_delete=models.CASCADE)
    fecha = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    def __str__(self):
        return f"Compra a {self.proveedor} - {self.fecha.date()}"

class CompraDetalle(models.Model):
    compra = models.ForeignKey(Compra, on_delete=models.CASCADE, related_name='detalles')
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField()
    precio_unitario = models.DecimalField(max_digits=8, decimal_places=2)
    def subtotal(self):
        return self.cantidad * self.precio_unitario

class Venta(models.Model):
    cliente = models.CharField(max_length=200)
    fecha = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    vendedor = models.ForeignKey(User, on_delete=models.CASCADE)
    def __str__(self):
        return f"Venta a {self.cliente} - {self.fecha.date()}"

class VentaDetalle(models.Model):
    venta = models.ForeignKey(Venta, on_delete=models.CASCADE, related_name='detalles')
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField()
    precio_unitario = models.DecimalField(max_digits=8, decimal_places=2)
    def subtotal(self):
        return self.cantidad * self.precio_unitario

# ========== EXTENSIÓN DE USUARIO (PERFIL) ==========
class Perfil(models.Model):
    ROLES = (
        ('admin', 'Administrador'),
        ('vendedor', 'Vendedor'),
    )
    ESTADOS = (
        ('activo', 'Activo'),
        ('inactivo', 'Inactivo'),
        ('suspendido', 'Suspendido'),
    )
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil')
    rol = models.CharField(max_length=20, choices=ROLES, default='vendedor')
    estado = models.CharField(max_length=20, choices=ESTADOS, default='activo')
    telefono = models.CharField(max_length=15, blank=True, null=True)
    def __str__(self):
        return f"{self.usuario.username} - {self.get_rol_display()} ({self.get_estado_display()})"

# Señales para crear y guardar el perfil automáticamente
@receiver(post_save, sender=User)
def crear_perfil(sender, instance, created, **kwargs):
    if created:
        Perfil.objects.get_or_create(usuario=instance)

