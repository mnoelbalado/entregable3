
from modelo import Producto, Condicion, Promocion


class DSLSupermercado:
    def __init__(self, supermercado):
        self.supermercado = supermercado
        self.producto_actual = None
        self.promocion_actual = None
        self.condicion_actual = None
        self.tipo_actual = None

    def _guardar_actual(self):
        if self.tipo_actual == "producto":
            datos = self.producto_actual

            if datos is not None:
                if datos["nombre"] is None or datos["precio"] is None:
                    raise ValueError(
                        "El producto necesita nombre y precio"
                    )

                producto = Producto(
                    datos["codigo"],
                    datos["nombre"],
                    datos["precio"],
                    datos["categoria"]
                )
                self.supermercado.agregar_producto(producto)

            self.producto_actual = None

        elif self.tipo_actual == "promocion":
            datos = self.promocion_actual

            if datos is not None:
                if datos["nombre"] is None or datos["descuento"] is None:
                    raise ValueError(
                        "La promoción necesita nombre y descuento"
                    )

                if not datos["condiciones"]:
                    raise ValueError(
                        "La promoción necesita al menos una condición"
                    )

                promocion = Promocion(
                    datos["codigo"],
                    datos["nombre"],
                    datos["descuento"],
                    datos["condiciones"]
                )
                self.supermercado.agregar_promocion(promocion)

            self.promocion_actual = None

        self.condicion_actual = None
        self.tipo_actual = None

    def producto(self, codigo):
        self._guardar_actual()

        self.producto_actual = {
            "codigo": codigo,
            "nombre": None,
            "precio": None,
            "categoria": None
        }
        self.tipo_actual = "producto"
        return self

    def promocion(self, codigo):
        self._guardar_actual()

        self.promocion_actual = {
            "codigo": codigo,
            "nombre": None,
            "descuento": None,
            "condiciones": []
        }
        self.tipo_actual = "promocion"
        return self

    def nombre(self, nombre):
        if self.tipo_actual == "producto":
            self.producto_actual["nombre"] = nombre
        elif self.tipo_actual == "promocion":
            self.promocion_actual["nombre"] = nombre
        else:
            raise ValueError("No hay producto o promoción activa")

        return self

    def precio(self, precio):
        if self.tipo_actual != "producto":
            raise ValueError("No hay un producto activo")

        self.producto_actual["precio"] = precio
        return self

    def categoria(self, categoria):
        if self.tipo_actual != "producto":
            raise ValueError("No hay un producto activo")

        self.producto_actual["categoria"] = categoria
        return self

    def descuento(self, porcentaje):
        if self.promocion_actual is None:
            raise ValueError("No hay una promoción activa")

        self.promocion_actual["descuento"] = porcentaje
        self.tipo_actual = "promocion"
        return self

    def cuando_producto(self, codigo):
        if self.promocion_actual is None:
            raise ValueError("No hay una promoción activa")

        condicion = Condicion(codigo)
        self.promocion_actual["condiciones"].append(condicion)
        self.condicion_actual = condicion
        self.tipo_actual = "condicion"
        return self

    def cantidad_igual(self, cantidad):
        if self.condicion_actual is None:
            raise ValueError("No hay una condición activa")

        self.condicion_actual.operador = "="
        self.condicion_actual.cantidad = cantidad
        self.tipo_actual = "promocion"
        return self

    def cantidad_mayor_igual(self, cantidad):
        if self.condicion_actual is None:
            raise ValueError("No hay una condición activa")

        self.condicion_actual.operador = ">="
        self.condicion_actual.cantidad = cantidad
        self.tipo_actual = "promocion"
        return self

    def finalizar(self):
        self._guardar_actual()
        return self.supermercado
