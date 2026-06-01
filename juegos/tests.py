from django.test import TestCase
from .models import Juego

class JuegoModelTest(TestCase):
    def test_str(self):
        juego = Juego(titulo="Mi Juego")
        self.assertEqual(str(juego), "Mi Juego")
