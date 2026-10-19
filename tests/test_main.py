import unittest

from main import (
    cargar_datos_iniciales,
    ejecutar_menu,
    mostrar_compras,
    mostrar_productos,
    mostrar_promociones,
    procesar_archivo,
)
from modelo import Producto
from supermercado import Supermercado


class TestMain(unittest.TestCase):
    def setUp(self):
        self.supermercado = cargar_datos_iniciales(Supermercado())

    def test_carga_inicial_se_realiza_con_dsl_interno(self):
        self.assertEqual(len(self.supermercado.productos), 4)
        self.assertEqual(len(self.supermercado.promociones), 2)
        self.assertEqual(self.supermercado.productos[3].nombre, "Refresco")
        self.assertEqual(
            self.supermercado.promociones[2].condiciones[0].cantidad,
            1,
        )

    def test_listado_de_productos_incluye_todos_los_campos(self):
        salida = []

        mostrar_productos(self.supermercado, salida.append)

        texto = "\n".join(salida)
        self.assertIn("Codigo: 1", texto)
        self.assertIn("Nombre: Arroz", texto)
        self.assertIn("Precio: 50", texto)
        self.assertIn("Categoria: Comestible", texto)
        self.assertIn("Categoria: Sin categoria", texto)

    def test_listado_de_promociones_incluye_condiciones(self):
        salida = []

        mostrar_promociones(self.supermercado, salida.append)

        texto = "\n".join(salida)
        self.assertIn("Codigo: 1", texto)
        self.assertIn("Nombre: Harina x5", texto)
        self.assertIn("Descuento: 20%", texto)
        self.assertIn("Producto 2 - Harina", texto)
        self.assertIn("Cantidad >= 5", texto)

    def test_listado_de_compras_muestra_lineas_promociones_y_total(self):
        self.supermercado.realizar_compra({3: 1, 4: 2})
        salida = []

        mostrar_compras(self.supermercado, salida.append)

        texto = "\n".join(salida)
        self.assertIn("Compra 1", texto)
        self.assertIn("Producto 3 - Refresco", texto)
        self.assertIn("Precio unitario: 100", texto)
        self.assertIn("Descuento: 25%", texto)
        self.assertIn("2 - 2 pizzas + refresco", texto)
        self.assertIn("Importe total: 300.0", texto)

    def test_compra_conserva_nombre_si_producto_se_elimina(self):
        self.supermercado.agregar_producto(Producto(5, "Temporal", 10))
        self.supermercado.realizar_compra({5: 1})
        self.supermercado.eliminar_producto(5)
        salida = []

        mostrar_compras(self.supermercado, salida.append)

        self.assertIn("Producto 5 - Temporal", "\n".join(salida))

    def test_menu_maneja_opcion_invalida_listados_y_salida(self):
        opciones = iter(["desconocida", "3", "4", "5", "0"])
        salida = []

        ejecutar_menu(
            self.supermercado,
            entrada=lambda _mensaje: next(opciones),
            salida=salida.append,
        )

        texto = "\n".join(salida)
        self.assertIn("Opcion invalida", texto)
        self.assertIn("Productos:", texto)
        self.assertIn("Promociones:", texto)
        self.assertIn("No hay compras registradas", texto)
        self.assertIn("Programa finalizado", texto)

    def test_procesar_archivo_informa_errores(self):
        class DSLFalso:
            @staticmethod
            def procesar_archivo(_ruta):
                return ["Error de prueba"]

        salida = []
        resultado = procesar_archivo(DSLFalso(), "entrada.txt", salida.append)

        self.assertFalse(resultado)
        self.assertIn("Error de prueba", "\n".join(salida))

    def test_procesar_archivo_maneja_error_de_lectura(self):
        class DSLFalso:
            @staticmethod
            def procesar_archivo(_ruta):
                raise FileNotFoundError("no existe")

        salida = []
        resultado = procesar_archivo(DSLFalso(), "inexistente", salida.append)

        self.assertFalse(resultado)
        self.assertIn("No se pudo leer", "\n".join(salida))


if __name__ == "__main__":
    unittest.main()
