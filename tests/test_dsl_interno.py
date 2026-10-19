import unittest

from dsl.dsl_interno import DSLSupermercado
from supermercado import Supermercado


class TestDSLInterno(unittest.TestCase):
    def setUp(self):
        self.supermercado = Supermercado()
        self.dsl = DSLSupermercado(self.supermercado)

    def test_carga_productos_con_atributos_en_distinto_orden(self):
        resultado = (
            self.dsl
            .producto(1)
                .categoria("Comestible")
                .precio(50)
                .nombre("Arroz")
            .producto(2)
                .precio(30)
                .nombre("Harina")
            .finalizar()
        )

        self.assertIs(resultado, self.supermercado)
        self.assertEqual(self.supermercado.productos[1].nombre, "Arroz")
        self.assertEqual(self.supermercado.productos[2].precio, 30)

    def test_condicion_sin_cantidad_usa_uno_y_guarda_promocion(self):
        (
            self.dsl
            .producto(1)
                .nombre("Arroz")
                .precio(50)
            .promocion(1)
                .descuento(10)
                .cuando_producto(1)
                .nombre("Descuento arroz")
            .finalizar()
        )

        promocion = self.supermercado.promociones[1]
        self.assertEqual(promocion.nombre, "Descuento arroz")
        self.assertEqual(promocion.condiciones[0].operador, "=")
        self.assertEqual(promocion.condiciones[0].cantidad, 1)

    def test_finaliza_directamente_despues_de_condicion(self):
        (
            self.dsl
            .producto(1).nombre("Arroz").precio(50)
            .promocion(1)
                .nombre("Descuento arroz")
                .descuento(10)
                .cuando_producto(1)
            .finalizar()
        )

        self.assertIn(1, self.supermercado.promociones)
        condicion = self.supermercado.promociones[1].condiciones[0]
        self.assertEqual(condicion.cantidad, 1)

    def test_promocion_admite_varias_condiciones_y_orden_libre(self):
        (
            self.dsl
            .producto(1).nombre("Pizza").precio(150)
            .producto(2).nombre("Refresco").precio(100)
            .promocion(1)
                .cuando_producto(2)
                .cuando_producto(1).cantidad_igual(2)
                .descuento(25)
                .nombre("2 pizzas + refresco")
            .finalizar()
        )

        promocion = self.supermercado.promociones[1]
        self.assertEqual(len(promocion.condiciones), 2)
        self.assertEqual(promocion.condiciones[0].cantidad, 1)
        self.assertEqual(promocion.condiciones[1].cantidad, 2)

    def test_cantidad_mayor_igual_conserva_operador(self):
        (
            self.dsl
            .producto(1).nombre("Harina").precio(30)
            .promocion(1)
                .nombre("Harina x5")
                .cuando_producto(1).cantidad_mayor_igual(5)
                .descuento(20)
            .finalizar()
        )

        condicion = self.supermercado.promociones[1].condiciones[0]
        self.assertEqual(condicion.operador, ">=")
        self.assertEqual(condicion.cantidad, 5)

    def test_rechaza_cantidad_invalida(self):
        (
            self.dsl
            .producto(1)
                .nombre("Harina")
                .precio(30)
            .finalizar()
        )

        with self.assertRaises(ValueError):
            (
                self.dsl
                .promocion(1)
                    .nombre("Invalida")
                    .descuento(10)
                    .cuando_producto(1)
                    .cantidad_igual(0)
            )

    def test_rechaza_entidades_incompletas(self):
        with self.assertRaises(ValueError):
            self.dsl.producto(1).nombre("Sin precio").finalizar()

        self.assertEqual(self.supermercado.productos, {})


if __name__ == "__main__":
    unittest.main()
