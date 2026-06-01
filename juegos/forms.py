from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User, Group
from .models import Perfil
from .models import Producto
from .models import Compra, Proveedor

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, label="Correo electrónico")
    rol = forms.ChoiceField(choices=Perfil.ROLES, required=True, label="Rol")
    estado = forms.ChoiceField(choices=Perfil.ESTADOS, required=True, label="Estado")

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2', 'rol', 'estado')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        
        # Asignar permisos según el rol seleccionado
        rol = self.cleaned_data['rol']
        if rol == 'admin':
            user.is_staff = True      # Acceso al admin de Django
            user.is_superuser = True  # Opcional: todos los permisos
        else:
            user.is_staff = False
            user.is_superuser = False
        
        if commit:
            user.save()
            # Crear o actualizar perfil
            perfil, created = Perfil.objects.get_or_create(usuario=user)
            perfil.rol = rol
            perfil.estado = self.cleaned_data['estado']
            perfil.save()
            
            # Asignar grupo correspondiente (opcional, pero útil para las vistas)
            grupo, _ = Group.objects.get_or_create(name=rol.capitalize())
            user.groups.add(grupo)
        
        return user
    
class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ['nombre', 'descripcion', 'precio_compra', 'precio_venta', 'stock', 'imagen']
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 3}),
        }


class CompraForm(forms.ModelForm):
    class Meta:
        model = Compra
        fields = ['proveedor']
        widgets = {
            'proveedor': forms.Select(attrs={'class': 'w-full bg-gray-700 border border-gray-600 text-white px-4 py-3 rounded-lg'})
        }        
