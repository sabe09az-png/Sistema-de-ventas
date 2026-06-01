from django.urls import path
from django.contrib.auth import views as auth_views
from . import views_inventario

urlpatterns = [
    # Página principal
    path('', views_inventario.dashboard, name='index'),
    path('dashboard/', views_inventario.dashboard, name='dashboard'),
    
    # Productos
    path('productos/', views_inventario.listar_productos, name='listar_productos'),
    path('productos/nuevo/', views_inventario.crear_producto, name='crear_producto'),
    path('productos/editar/<int:pk>/', views_inventario.editar_producto, name='editar_producto'),
    path('productos/eliminar/<int:pk>/', views_inventario.eliminar_producto, name='eliminar_producto'),
    path('productos/stock/<int:pk>/', views_inventario.actualizar_stock, name='actualizar_stock'),
    
    # Compras y Ventas
    path('compra/', views_inventario.registrar_compra, name='registrar_compra'),
    path('venta/', views_inventario.registrar_venta, name='registrar_venta'),
    path('historial-compras/', views_inventario.historial_compras, name='historial_compras'),
    path('historial-ventas/', views_inventario.historial_ventas, name='historial_ventas'),
    
    # Proveedores
    path('proveedor/crear/', views_inventario.crear_proveedor, name='crear_proveedor'),
    path('test/', views_inventario.home_test, name='test'),
    
    # Autenticación
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/login/'), name='logout'),
    path('registro/', views_inventario.registro, name='registro'),
]