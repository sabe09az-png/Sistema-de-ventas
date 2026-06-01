from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.urls import reverse
from django.conf import settings
from django.http import JsonResponse
from .models import *
from paypal.standard.forms import PayPalPaymentsForm
from django.core.exceptions import PermissionDenied
from .models import Perfil
from django.contrib import messages
##from django.contrib.auth.forms import UserCreationForm
from .forms import CustomUserCreationForm

def index(request):
    juegos_destacados = Juego.objects.all()[:6]
    top10_descargas = Juego.objects.order_by('-descargas')[:10]
    return render(request, 'juegos/index.html', {
        'juegos_destacados': juegos_destacados,
        'top10_descargas': top10_descargas,
    })

def juegos_lista(request):
    juegos = Juego.objects.all()
    
    # Obtener juegos que el usuario ya tiene en biblioteca y carrito
    user_juegos_comprados = []
    user_juegos_carrito = []
    
    if request.user.is_authenticated:
        user_juegos_comprados = [bj.juego for bj in BibliotecaJuego.objects.filter(usuario=request.user)]
        user_juegos_carrito = [ci.juego for ci in CarritoItem.objects.filter(carrito__usuario=request.user)]
    
    return render(request, "juegos/juegos_lista.html", {
        "juegos": juegos,
        "user_juegos_comprados": user_juegos_comprados,
        "user_juegos_carrito": user_juegos_carrito,
    })

def juego_detalle(request, pk):
    juego = get_object_or_404(Juego, pk=pk)
    
    # Obtener juegos que el usuario ya tiene en biblioteca y carrito
    user_juegos_comprados = []
    user_juegos_carrito = []
    
    if request.user.is_authenticated:
        user_juegos_comprados = [bj.juego for bj in BibliotecaJuego.objects.filter(usuario=request.user)]
        user_juegos_carrito = [ci.juego for ci in CarritoItem.objects.filter(carrito__usuario=request.user)]
    
    return render(request, "juegos/detalle_juego.html", {
        "juego": juego,
        "user_juegos_comprados": user_juegos_comprados,
        "user_juegos_carrito": user_juegos_carrito,
    })

def lista_colecciones(request):
    colecciones = Coleccion.objects.all()
    return render(request, 'juegos/colecciones.html', {'colecciones': colecciones})

def coleccion_detalle(request, coleccion_id):
    coleccion = get_object_or_404(Coleccion, id=coleccion_id)
    juegos = Juego.objects.filter(coleccion=coleccion)
    
    # DEBUG DETALLADO
    print("=" * 50)
    print(f"🎯 COLECCIÓN: {coleccion.nombre} (ID: {coleccion.id})")
    print(f"📊 TOTAL JUEGOS EN BD: {Juego.objects.count()}")
    print(f"🔍 JUEGOS EN ESTA COLECCIÓN: {juegos.count()}")
    
    # Ver todos los juegos en la colección
    for juego in juegos:
        print(f"   ✅ {juego.titulo} - Colección: {juego.coleccion}")
    
    # Verificar si hay problemas con los juegos
    todos_los_juegos = Juego.objects.all()
    print(f"📋 TODOS LOS JUEGOS EN BD:")
    for juego in todos_los_juegos:
        print(f"   🎮 {juego.titulo} - Colección: {juego.coleccion}")
    
    print("=" * 50)
    
    return render(request, 'juegos/coleccion_detalle.html', {
        'coleccion': coleccion,
        'juegos': juegos
    })

def ayuda(request):
    preguntas = [
        {"pregunta": "¿Cómo comprar un juego?", "respuesta": "Agrega juegos al carrito y procede al pago con PayPal."},
        {"pregunta": "¿Necesito cuenta?", "respuesta": "Sí, necesitas una cuenta para comprar y acceder a tu biblioteca."},
    ]
    return render(request, 'juegos/ayuda.html', {'preguntas': preguntas})

def registro(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, '¡Cuenta creada exitosamente!')
            return redirect('dashboard')
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/registro.html', {'form': form})

@login_required
def agregar_al_carrito(request, juego_id):
    juego = get_object_or_404(Juego, id=juego_id)
    carrito, created = Carrito.objects.get_or_create(usuario=request.user)
    
    # VERIFICAR SI EL USUARIO YA TIENE EL JUEGO EN SU BIBLIOTECA
    if BibliotecaJuego.objects.filter(usuario=request.user, juego=juego).exists():
        messages.warning(request, f'Ya tienes "{juego.titulo}" en tu biblioteca')
        return redirect('juegos_lista')
    
    # VERIFICAR SI EL JUEGO YA ESTÁ EN EL CARRITO (evitar duplicados)
    item_existente = CarritoItem.objects.filter(carrito=carrito, juego=juego).first()
    
    if item_existente:
        messages.info(request, f'"{juego.titulo}" ya está en tu carrito')
        return redirect('juegos_lista')
    
    # AGREGAR AL CARRITO (solo si no existe)
    CarritoItem.objects.create(carrito=carrito, juego=juego, cantidad=1)
    
    messages.success(request, f'"{juego.titulo}" agregado al carrito')
    return redirect('juegos_lista')

@login_required
def ver_carrito(request):
    carrito, created = Carrito.objects.get_or_create(usuario=request.user)
    return render(request, 'juegos/carrito.html', {'carrito': carrito})

@login_required
def eliminar_del_carrito(request, item_id):
    item = get_object_or_404(CarritoItem, id=item_id, carrito__usuario=request.user)
    juego_titulo = item.juego.titulo
    item.delete()
    messages.success(request, f'"{juego_titulo}" eliminado del carrito')
    return redirect('ver_carrito')

@login_required
def procesar_pago(request):
    carrito = Carrito.objects.get(usuario=request.user)
    
    if carrito.items.count() == 0:
        messages.error(request, 'Tu carrito está vacío')
        return redirect('ver_carrito')
    
    # Crear orden
    orden = Orden.objects.create(
        usuario=request.user,
        total=carrito.total()
    )
    
    # Crear items de la orden
    for item in carrito.items.all():
        OrdenItem.objects.create(
            orden=orden,
            juego=item.juego,
            precio=item.juego.precio,
            cantidad=item.cantidad
        )
    
    # Configurar PayPal
    paypal_dict = {
        "business": settings.PAYPAL_RECEIVER_EMAIL,
        "amount": str(orden.total),
        "item_name": f"Orden #{orden.id} - Game-zher",
        "invoice": f"orden-{orden.id}",
        "currency_code": "USD",
        "notify_url": request.build_absolute_uri(reverse('paypal-ipn')),
        "return_url": request.build_absolute_uri(reverse('pago_completado')),
        "cancel_return": request.build_absolute_uri(reverse('pago_cancelado')),
    }
    
    form = PayPalPaymentsForm(initial=paypal_dict)
    
    return render(request, 'juegos/procesar_pago.html', {
        'orden': orden,
        'form': form,
        'carrito': carrito
    })

@login_required
def pago_completado(request):
    carrito = Carrito.objects.get(usuario=request.user)
    
    # Aquí procesarías la orden como completada cuando PayPal confirme
    # Por ahora simulamos que se completó
    orden = Orden.objects.filter(usuario=request.user).last()
    if orden:
        orden.estado = 'completada'
        orden.save()
        
        # Agregar juegos a la biblioteca
        for item in orden.items.all():
            BibliotecaJuego.objects.get_or_create(
                usuario=request.user,
                juego=item.juego,
                orden=orden
            )
    
    carrito.items.all().delete()
    
    messages.success(request, '¡Pago completado! Los juegos están en tu biblioteca')
    return render(request, 'juegos/pago_completado.html')

@login_required
def pago_cancelado(request):
    messages.error(request, 'El pago fue cancelado')
    return render(request, 'juegos/pago_cancelado.html')

@login_required
def biblioteca(request):
    juegos_comprados = BibliotecaJuego.objects.filter(usuario=request.user)
    return render(request, 'juegos/biblioteca.html', {'juegos_comprados': juegos_comprados})

@login_required
def descargar_juego(request, juego_id):
    juego = get_object_or_404(Juego, id=juego_id)
    
    # Verificar que el usuario haya comprado el juego
    if not BibliotecaJuego.objects.filter(usuario=request.user, juego=juego).exists():
        messages.error(request, 'No has comprado este juego')
        return redirect('biblioteca')
    
    # Incrementar descargas (esto activará el signal automáticamente)
    juego.descargas += 1
    juego.save()
    
    if juego.archivo_juego:
        return redirect(juego.archivo_juego.url)
    else:
        messages.error(request, 'Archivo no disponible')
        return redirect('biblioteca')

# Context processor para el carrito
def carrito_context(request):
    if request.user.is_authenticated:
        try:
            carrito = Carrito.objects.get(usuario=request.user)
            carrito_count = carrito.items.count()
        except Carrito.DoesNotExist:
            carrito_count = 0
    else:
        carrito_count = 0
    
    return {'carrito_count': carrito_count}


def admin_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if not (request.user.is_superuser or request.user.groups.filter(name='Administrador').exists()):
            raise PermissionDenied
        return view_func(request, *args, **kwargs)
    return wrapper
