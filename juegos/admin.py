from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import Proveedor, Producto, Compra, CompraDetalle, Venta, VentaDetalle, Perfil

# Inline para mostrar el perfil dentro del UserAdmin
class PerfilInline(admin.StackedInline):
    model = Perfil
    can_delete = False
    fields = ('rol', 'estado', 'telefono')

# Personalización del admin de usuarios
class CustomUserAdmin(UserAdmin):
    inlines = [PerfilInline]  # ← DESCOMENTADO para poder editar el perfil
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_active', 'get_rol', 'get_estado')
    
    def get_rol(self, obj):
        return obj.perfil.get_rol_display() if hasattr(obj, 'perfil') else 'Sin perfil'
    get_rol.short_description = 'Rol'
    get_rol.admin_order_field = 'perfil__rol'
    
    def get_estado(self, obj):
        return obj.perfil.get_estado_display() if hasattr(obj, 'perfil') else 'Sin perfil'
    get_estado.short_description = 'Estado'
    get_estado.admin_order_field = 'perfil__estado'
    
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        perfil, created = Perfil.objects.get_or_create(usuario=obj)
        # Los campos del inline se guardan automáticamente, esto es solo por seguridad
        if not created and hasattr(obj, 'perfil'):
            pass  # Los inline ya guardan los datos

# Reemplazar el UserAdmin por defecto
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

# ========== MODELOS DEL SISTEMA DE GESTIÓN ==========
@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'precio_compra', 'precio_venta', 'stock')
    search_fields = ('nombre',)

@admin.register(Proveedor)
class ProveedorAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'contacto', 'telefono', 'email')
    search_fields = ('nombre',)

class CompraDetalleInline(admin.TabularInline):
    model = CompraDetalle
    extra = 1

@admin.register(Compra)
class CompraAdmin(admin.ModelAdmin):
    list_display = ('id', 'proveedor', 'fecha', 'total', 'usuario')
    inlines = [CompraDetalleInline]

class VentaDetalleInline(admin.TabularInline):
    model = VentaDetalle
    extra = 1

@admin.register(Venta)
class VentaAdmin(admin.ModelAdmin):
    list_display = ('id', 'cliente', 'fecha', 'total', 'vendedor')
    inlines = [VentaDetalleInline]