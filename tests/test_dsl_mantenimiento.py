import tempfile
import unittest
from pathlib import Path

from dsl.dsl_mantenimiento import DSLMantenimiento
from modelo import Condicion, Producto, Promocion
from supermercado import Supermercado


class TestDSLMantenimiento(unittest.TestCase):
    def setUp(self):
        self.supermercado = Supermercado()
        for producto in [
            Producto(1, "Arroz", 50, "Comestible"),
            Producto(2, "Harina", 30),
            Producto(3, "Refresco", 100, "Bebida"),
            Producto(4, "Pizza", 150),
        ]:
            self.supermercado.agregar_producto(producto)
        self.supermercado.agregar_promocion(
            Promocion(
                1,
                "Harina x5",
                20,
                [Condicion(2, ">=", 5)],
            )
        )
        self.supermercado.agregar_promocion(
            Promocion(
                2,
                "2 pizzas + refresco",
                25,
                [Condicion(3), Condicion(4, "=", 2)],
            )
        )
        self.dsl = DSLMantenimiento(self.supermercado)

    def test_procesa_ejemplo_completo_de_la_letra(self):
        texto = """
        AGREGAR PRODUCTO 5
          NOMBRE “Azucar”
          PRECIO 60
          CATEGORIA “Comestible”
        FIN
        AGREGAR PRODUCTO 6
          PRECIO 45
          NOMBRE "Leche"
        FIN
        ACTUALIZAR PRODUCTO 3
          NOMBRE "Coca Cola"
        FIN
        ACTUALIZAR PRODUCTO 2
          CATEGORIA "Comestible"
          PRECIO 35.5
        FIN
        ACTUALIZAR PROMOCION 1
          CUANDO
            PRODUCTO 2 CANTIDAD >= 3
          NOMBRE "Harina x3"
        FIN
        AGREGAR PROMOCION 3
          DESCUENTO 30.5
          NOMBRE "Leche + Azucar"
          CUANDO
            PRODUCTO 6
            PRODUCTO 5 CANTIDAD = 1
        FIN
        ELIMINAR PRODUCTO 1
        ELIMINAR PROMOCION 2
        """

        errores = self.dsl.procesar(texto)

        self.assertEqual(errores, [])
        self.assertEqual(self.supermercado.productos[5].nombre, "Azucar")
        self.assertEqual(self.supermercado.productos[6].categoria, None)
        self.assertEqual(self.supermercado.productos[3].nombre, "Coca Cola")
        self.assertEqual(self.supermercado.productos[2].precio, 35.5)
        self.assertNotIn(1, self.supermercado.productos)
        self.assertNotIn(2, self.supermercado.promociones)

        promocion = self.supermercado.promociones[1]
        self.assertEqual(promocion.nombre, "Harina x3")
        self.assertEqual(len(promocion.condiciones), 1)
        self.assertEqual(promocion.condiciones[0].cantidad, 3)
        self.assertEqual(promocion.condiciones[0].operador, ">=")

        nueva = self.supermercado.promociones[3]
        self.assertEqual(nueva.descuento, 30.5)
        self.assertEqual(len(nueva.condiciones), 2)
        self.assertEqual(nueva.condiciones[0].cantidad, 1)

    def test_error_semantico_no_detiene_operaciones_siguientes(self):
        texto = """
        AGREGAR PRODUCTO 1
          NOMBRE "Duplicado"
          PRECIO 10
        FIN
        AGREGAR PRODUCTO 7
          NOMBRE "Valido"
          PRECIO 12.25
        FIN
        ELIMINAR PRODUCTO 99
        ACTUALIZAR PRODUCTO 7
          CATEGORIA "Nuevo"
        FIN
        AGREGAR PRODUCTO 8
        FIN
        AGREGAR PRODUCTO 9
          NOMBRE "Tambien valido"
          PRECIO 15
        FIN
        """

        errores = self.dsl.procesar(texto)

        self.assertEqual(len(errores), 3)
        self.assertIn("Ya existe el producto 1", errores[0])
        self.assertIn("No existe el producto 99", errores[1])
        self.assertIn("nombre del producto debe ser texto", errores[2])
        self.assertEqual(self.supermercado.productos[7].categoria, "Nuevo")
        self.assertIn(9, self.supermercado.productos)

    def test_reemplaza_condiciones_solo_si_aparece_cuando(self):
        sin_cuando = """
        ACTUALIZAR PROMOCION 1
          NOMBRE "Nombre nuevo"
        FIN
        """
        self.assertEqual(self.dsl.procesar(sin_cuando), [])
        self.assertEqual(self.supermercado.promociones[1].condiciones[0].cantidad, 5)

        con_cuando = """
        ACTUALIZAR PROMOCION 1
          CUANDO
            PRODUCTO 2 CANTIDAD = 2
        FIN
        """
        self.assertEqual(self.dsl.procesar(con_cuando), [])
        condicion = self.supermercado.promociones[1].condiciones[0]
        self.assertEqual(condicion.cantidad, 2)
        self.assertEqual(condicion.operador, "=")

    def test_informa_error_sintactico_con_ubicacion(self):
        errores = self.dsl.procesar(
            "AGREGAR PRODUCTO 8 NOMBRE \"Sin fin\" PRECIO 10"
        )

        self.assertEqual(len(errores), 1)
        self.assertIn("Error sintactico", errores[0])
        self.assertIn("linea", errores[0])
        self.assertNotIn(8, self.supermercado.productos)

    def test_valida_campos_y_condiciones_duplicadas(self):
        texto = """
        AGREGAR PRODUCTO 8
          NOMBRE "Precio invalido"
          PRECIO 1.234
        FIN
        AGREGAR PROMOCION 8
          NOMBRE "Duplicada"
          DESCUENTO 10
          CUANDO
            PRODUCTO 2
            PRODUCTO 2 CANTIDAD = 2
        FIN
        AGREGAR PRODUCTO 9
          NOMBRE "Correcto"
          PRECIO 9.99
        FIN
        """

        errores = self.dsl.procesar(texto)

        self.assertEqual(len(errores), 2)
        self.assertNotIn(8, self.supermercado.productos)
        self.assertNotIn(8, self.supermercado.promociones)
        self.assertIn(9, self.supermercado.productos)

    def test_procesa_archivo_utf8(self):
        texto = """
        AGREGAR PRODUCTO 10
          NOMBRE "Cafe"
          PRECIO 20
          CATEGORIA "Almacen"
        FIN
        """
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as directorio:
            ruta = Path(directorio) / "mantenimiento.txt"
            ruta.write_text(texto, encoding="utf-8")
            errores = self.dsl.procesar_archivo(ruta)

        self.assertEqual(errores, [])
        self.assertEqual(self.supermercado.productos[10].nombre, "Cafe")


if __name__ == "__main__":
    unittest.main()
