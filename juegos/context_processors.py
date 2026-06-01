from .models import Carrito

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