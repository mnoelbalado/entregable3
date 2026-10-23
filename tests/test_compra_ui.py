import unittest

from compra_ui import PantallaCompra
from main import cargar_datos_iniciales
from supermercado import Supermercado


class TestAvisosPromociones(unittest.TestCase):
    def setUp(self):
        self.pantalla = PantallaCompra.__new__(PantallaCompra)
        self.pantalla.supermercado = cargar_datos_iniciales(Supermercado())
        self.pantalla.cantidades = {}

    def test_no_sugiere_promociones_con_el_carrito_vacio(self):
        aviso = self.pantalla._crear_aviso_promocion(set())

        self.assertEqual(aviso, "")

    def test_no_sugiere_promociones_para_un_producto_ajeno(self):
        self.pantalla.cantidades = {1: 1}

        aviso = self.pantalla._crear_aviso_promocion(set())

        self.assertEqual(aviso, "")

    def test_sugiere_promocion_al_agregar_un_producto_relacionado(self):
        self.pantalla.cantidades = {4: 1}

        aviso = self.pantalla._crear_aviso_promocion(set())

        self.assertIn("2 pizzas + refresco", aviso)
        self.assertIn("1 unidad de Refresco", aviso)
        self.assertIn("1 unidad de Pizza", aviso)

    def test_informa_solamente_lo_que_falta(self):
        self.pantalla.cantidades = {3: 1, 4: 1}

        aviso = self.pantalla._crear_aviso_promocion(set())

        self.assertIn("1 unidad de Pizza", aviso)
        self.assertNotIn("Refresco", aviso)

    def test_no_sugiere_una_promocion_ajena_tras_aplicar_otra(self):
        self.pantalla.cantidades = {3: 1, 4: 2}

        aviso = self.pantalla._crear_aviso_promocion({2})

        self.assertEqual(aviso, "")


if __name__ == "__main__":
    unittest.main()
