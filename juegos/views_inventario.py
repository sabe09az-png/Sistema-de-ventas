from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.db import transaction
from django.utils import timezone
from django.contrib.auth import logout, login
from datetime import datetime, time
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Producto, Compra, Venta, Perfil, CompraDetalle, VentaDetalle, Proveedor
from .forms import ProductoForm
from django.http import HttpResponse

# ========== REGISTRO ==========
def registro(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = UserCreationForm()
    return render(request, 'registration/registro.html', {'form': form})

# ========== LOGOUT ==========
def logout_view(request):
    logout(request)
    return redirect('login')

# ========== PRUEBA ==========
def home_test(request):
    return HttpResponse("¡La aplicación está funcionando correctamente!")

# ========== PROVEEDORES ==========
@login_required
@staff_member_required
def crear_proveedor(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        contacto = request.POST.get('contacto')
        telefono = request.POST.get('telefono')
        email = request.POST.get('email')
        
        if nombre:
            Proveedor.objects.create(
                nombre=nombre,
                contacto=contacto,
                telefono=telefono,
                email=email
            )
            messages.success(request, f'Proveedor "{nombre}" creado exitosamente')
            return redirect('registrar_compra')
        else:
            messages.error(request, 'El nombre del proveedor es obligatorio')
    
    return render(request, 'juegos/crear_proveedor.html')

# ========== DASHBOARD ==========
@login_required
def dashboard(request):
    es_admin = request.user.is_superuser or request.user.groups.filter(name='Administrador').exists()
    context = {}
    
    ahora = timezone.localtime(timezone.now())
    inicio_dia = datetime.combine(ahora.date(), time.min)
    fin_dia = datetime.combine(ahora.date(), time.max)
    
    inicio_dia = timezone.make_aware(inicio_dia)
    fin_dia = timezone.make_aware(fin_dia)
    
    if es_admin:
        context['productos_bajos'] = Producto.objects.filter(stock__lt=10)
        context['compras_recientes'] = Compra.objects.all().order_by('-fecha')[:5]
        context['ventas_hoy'] = Venta.objects.filter(fecha__range=(inicio_dia, fin_dia))
    else:
        context['productos_bajos'] = []
        context['compras_recientes'] = Compra.objects.none()
        context['ventas_hoy'] = Venta.objects.filter(vendedor=request.user, fecha__range=(inicio_dia, fin_dia))
    
    return render(request, 'juegos/dashboard.html', context)

# ========== PRODUCTOS ==========
@login_required
def listar_productos(request):
    productos = Producto.objects.all().order_by('nombre')
    return render(request, 'juegos/productos_lista.html', {'productos': productos})

@staff_member_required
def crear_producto(request):
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Producto creado exitosamente.')
            return redirect('listar_productos')
    else:
        form = ProductoForm()
    return render(request, 'juegos/producto_form.html', {'form': form, 'titulo': 'Crear Producto'})

@staff_member_required
def editar_producto(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES, instance=producto)
        if form.is_valid():
            form.save()
            messages.success(request, 'Producto actualizado.')
            return redirect('listar_productos')
    else:
        form = ProductoForm(instance=producto)
    return render(request, 'juegos/producto_form.html', {'form': form, 'titulo': 'Editar Producto'})

@staff_member_required
def eliminar_producto(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == 'POST':
        producto.delete()
        messages.success(request, 'Producto eliminado.')
        return redirect('listar_productos')
    return render(request, 'juegos/producto_confirm_delete.html', {'producto': producto})

@login_required
def actualizar_stock(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == 'POST':
        nuevo_stock = request.POST.get('stock')
        if nuevo_stock is not None:
            producto.stock = int(nuevo_stock)
            producto.save()
            messages.success(request, f'Stock de {producto.nombre} actualizado a {producto.stock}')
        return redirect('listar_productos')
    return render(request, 'juegos/actualizar_stock.html', {'producto': producto})

# ========== COMPRAS ==========
@login_required
@staff_member_required
def registrar_compra(request):
    if request.method == 'POST':
        proveedor_id = request.POST.get('proveedor')
        if not proveedor_id:
            messages.error(request, 'Debe seleccionar un proveedor')
            return redirect('registrar_compra')
        
        with transaction.atomic():
            compra = Compra.objects.create(
                proveedor_id=proveedor_id,
                usuario=request.user,
                total=0
            )
            total_compra = 0
            
            for key, value in request.POST.items():
                if key.startswith('cantidad_'):
                    producto_id = key.split('_')[1]
                    cantidad = int(value) if value else 0
                    if cantidad > 0:
                        producto = Producto.objects.get(id=producto_id)
                        precio_compra = float(request.POST.get(f'precio_{producto_id}', 0))
                        
                        if precio_compra <= 0:
                            messages.error(request, f'Debe ingresar un precio válido para {producto.nombre}')
                            return redirect('registrar_compra')
                        
                        CompraDetalle.objects.create(
                            compra=compra,
                            producto=producto,
                            cantidad=cantidad,
                            precio_unitario=precio_compra
                        )
                        producto.stock += cantidad
                        producto.precio_compra = precio_compra
                        producto.save()
                        total_compra += cantidad * precio_compra
            
            if total_compra == 0:
                messages.error(request, 'Debe seleccionar al menos un producto con cantidad > 0')
                compra.delete()
                return redirect('registrar_compra')
            
            compra.total = total_compra
            compra.save()
        
        messages.success(request, f'Compra registrada exitosamente. Total: ${total_compra}')
        return redirect('dashboard')
    
    else:
        productos = Producto.objects.all()
        proveedores = Proveedor.objects.all()
        return render(request, 'juegos/registrar_compra.html', {
            'productos': productos,
            'proveedores': proveedores
        })

# ========== VENTAS ==========
@login_required
def registrar_venta(request):
    if request.method == 'POST':
        cliente = request.POST.get('cliente')
        if not cliente:
            messages.error(request, 'Debe ingresar el nombre del cliente')
            return redirect('registrar_venta')

        with transaction.atomic():
            venta = Venta.objects.create(
                cliente=cliente,
                vendedor=request.user,
                total=0
            )
            total_venta = 0

            for key, value in request.POST.items():
                if key.startswith('cantidad_'):
                    producto_id = key.split('_')[1]
                    cantidad = int(value) if value else 0
                    if cantidad > 0:
                        producto = Producto.objects.get(id=producto_id)
                        if producto.stock < cantidad:
                            messages.error(request, f'Stock insuficiente para "{producto.nombre}". Disponible: {producto.stock}')
                            return redirect('registrar_venta')
                        
                        VentaDetalle.objects.create(
                            venta=venta,
                            producto=producto,
                            cantidad=cantidad,
                            precio_unitario=producto.precio_venta
                        )
                        producto.stock -= cantidad
                        producto.save()
                        total_venta += cantidad * producto.precio_venta

            if total_venta == 0:
                messages.error(request, 'Debe seleccionar al menos un producto con cantidad > 0')
                venta.delete()
                return redirect('registrar_venta')

            venta.total = total_venta
            venta.save()

        messages.success(request, f'Venta registrada exitosamente. Total: ${total_venta}')
        return redirect('dashboard')

    else:
        productos = Producto.objects.filter(stock__gt=0)
        return render(request, 'juegos/registrar_venta.html', {'productos': productos})

# ========== HISTORIALES ==========
@login_required
def historial_ventas(request):
    if request.user.is_superuser or request.user.groups.filter(name='Administrador').exists():
        ventas = Venta.objects.all().order_by('-fecha')
    else:
        ventas = Venta.objects.filter(vendedor=request.user).order_by('-fecha')
    
    fecha_desde = request.GET.get('fecha_desde')
    fecha_hasta = request.GET.get('fecha_hasta')
    vendedor_id = request.GET.get('vendedor')
    
    if fecha_desde:
        try:
            fecha_desde_obj = datetime.strptime(fecha_desde, '%Y-%m-%d').date()
            ventas = ventas.filter(fecha__date__gte=fecha_desde_obj)
        except:
            pass
    if fecha_hasta:
        try:
            fecha_hasta_obj = datetime.strptime(fecha_hasta, '%Y-%m-%d').date()
            ventas = ventas.filter(fecha__date__lte=fecha_hasta_obj)
        except:
            pass
    if vendedor_id and (request.user.is_superuser or request.user.groups.filter(name='Administrador').exists()):
        ventas = ventas.filter(vendedor_id=vendedor_id)
    
    vendedores = None
    if request.user.is_superuser or request.user.groups.filter(name='Administrador').exists():
        vendedores = User.objects.filter(groups__name='Vendedor') | User.objects.filter(is_superuser=True)
    
    context = {
        'ventas': ventas,
        'vendedores': vendedores,
        'fecha_desde': fecha_desde,
        'fecha_hasta': fecha_hasta,
        'vendedor_seleccionado': vendedor_id,
    }
    return render(request, 'juegos/historial_ventas.html', context)

@login_required
def historial_compras(request):
    if not (request.user.is_superuser or request.user.groups.filter(name='Administrador').exists()):
        messages.error(request, 'No tienes permiso para ver compras')
        return redirect('dashboard')
    
    compras = Compra.objects.all().order_by('-fecha')
    
    fecha_desde = request.GET.get('fecha_desde')
    fecha_hasta = request.GET.get('fecha_hasta')
    proveedor = request.GET.get('proveedor')
    
    if fecha_desde:
        try:
            compras = compras.filter(fecha__date__gte=datetime.strptime(fecha_desde, '%Y-%m-%d').date())
        except:
            pass
    if fecha_hasta:
        try:
            compras = compras.filter(fecha__date__lte=datetime.strptime(fecha_hasta, '%Y-%m-%d').date())
        except:
            pass
    if proveedor:
        compras = compras.filter(proveedor__nombre__icontains=proveedor)
    
    context = {
        'compras': compras,
        'fecha_desde': fecha_desde,
        'fecha_hasta': fecha_hasta,
        'proveedor': proveedor,
    }
    return render(request, 'juegos/historial_compras.html', context)