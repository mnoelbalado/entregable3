import tempfile
import unittest
from pathlib import Path

from dsl.dsl_compras import DSLCompras
from modelo import Condicion, Producto, Promocion
from supermercado import Supermercado


class TestDSLCompras(unittest.TestCase):
    def setUp(self):
        self.supermercado = Supermercado()
        for producto in [
            Producto(1, "Harina", 30),
            Producto(2, "Levadura", 10),
            Producto(3, "Azucar", 20),
        ]:
            self.supermercado.agregar_producto(producto)

        self.supermercado.agregar_promocion(
            Promocion(
                1,
                "Harina + levadura",
                30,
                [Condicion(1), Condicion(2)],
            )
        )
        self.supermercado.agregar_promocion(
            Promocion(
                2,
                "2 harinas + azucar",
                20,
                [Condicion(1, "=", 2), Condicion(3)],
            )
        )
        self.supermercado.agregar_promocion(
            Promocion(
                3,
                "4 harinas",
                10,
                [Condicion(1, "=", 4)],
            )
        )
        self.dsl = DSLCompras(self.supermercado)

    def test_procesa_los_seis_ejemplos_de_la_letra(self):
        texto = """
        COMPRA
          PRODUCTO 1 CANTIDAD 4
          PRODUCTO 2
        FIN
        COMPRA
          PRODUCTO 1 CANTIDAD 4
          PRODUCTO 2
          PRODUCTO 3
        FIN
        COMPRA
          PRODUCTO 1 CANTIDAD 4
        FIN
        COMPRA
          PRODUCTO 1
          PRODUCTO 3
        FIN
        COMPRA
          PRODUCTO 1 CANTIDAD 8
        FIN
        COMPRA
          PRODUCTO 1 CANTIDAD 6
        FIN
        """

        errores = self.dsl.procesar(texto)

        self.assertEqual(errores, [])
        self.assertEqual(len(self.supermercado.compras), 6)
        esperadas = [
            ([(1, 1, 30), (1, 3, 0), (2, 1, 30)], [1]),
            (
                [
                    (1, 1, 30),
                    (1, 2, 20),
                    (1, 1, 0),
                    (2, 1, 30),
                    (3, 1, 20),
                ],
                [1, 2],
            ),
            ([(1, 4, 10)], [3]),
            ([(1, 1, 0), (3, 1, 0)], []),
            ([(1, 8, 10)], [3]),
            ([(1, 4, 10), (1, 2, 0)], [3]),
        ]
        for compra, (lineas_esperadas, promociones_esperadas) in zip(
            self.supermercado.compras,
            esperadas,
        ):
            lineas = [
                (linea.codigo_producto, linea.cantidad, linea.descuento)
                for linea in compra.lineas
            ]
            promociones = [
                promocion.codigo
                for promocion in compra.promociones_aplicadas
            ]
            self.assertEqual(lineas, lineas_esperadas)
            self.assertEqual(promociones, promociones_esperadas)

    def test_cantidad_predeterminada_y_lineas_repetidas(self):
        errores = self.dsl.procesar(
            """
            COMPRA
              PRODUCTO 3
              PRODUCTO 3 CANTIDAD 2
            FIN
            """
        )

        self.assertEqual(errores, [])
        compra = self.supermercado.compras[0]
        self.assertEqual(len(compra.lineas), 1)
        self.assertEqual(compra.lineas[0].codigo_producto, 3)
        self.assertEqual(compra.lineas[0].cantidad, 3)

    def test_errores_semanticos_no_detienen_compras_siguientes(self):
        texto = """
        COMPRA
          PRODUCTO 99
        FIN
        COMPRA
        FIN
        COMPRA
          PRODUCTO 1 CANTIDAD 0
        FIN
        COMPRA
          PRODUCTO 3 CANTIDAD 2
        FIN
        """

        errores = self.dsl.procesar(texto)

        self.assertEqual(len(errores), 3)
        self.assertIn("No existe el producto 99", errores[0])
        self.assertIn("al menos un producto", errores[1])
        self.assertIn("mayor que cero", errores[2])
        self.assertEqual(len(self.supermercado.compras), 1)
        self.assertEqual(self.supermercado.compras[0].lineas[0].cantidad, 2)

    def test_error_en_una_compra_no_deja_resultado_parcial(self):
        errores = self.dsl.procesar(
            """
            COMPRA
              PRODUCTO 1 CANTIDAD 2
              PRODUCTO 99
            FIN
            """
        )

        self.assertEqual(len(errores), 1)
        self.assertEqual(self.supermercado.compras, [])

    def test_informa_error_sintactico_con_ubicacion(self):
        errores = self.dsl.procesar(
            "COMPRA PRODUCTO 1 CANTIDAD DOS FIN"
        )

        self.assertEqual(len(errores), 1)
        self.assertIn("Error sintactico", errores[0])
        self.assertIn("linea", errores[0])
        self.assertEqual(self.supermercado.compras, [])

    def test_procesa_archivo_utf8(self):
        texto = """
        COMPRA
          PRODUCTO 1
          PRODUCTO 2
        FIN
        """
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as directorio:
            ruta = Path(directorio) / "compras.txt"
            ruta.write_text(texto, encoding="utf-8")
            errores = self.dsl.procesar_archivo(ruta)

        self.assertEqual(errores, [])
        self.assertEqual(len(self.supermercado.compras), 1)


if __name__ == "__main__":
    unittest.main()
