from modelo import Condicion, Producto, Promocion


class DSLSupermercado:
    def __init__(self, supermercado):
        self.supermercado = supermercado

    def producto(self, codigo):
        return ProductoBuilder(self, codigo)

    def promocion(self, codigo):
        return PromocionBuilder(self, codigo)

    def finalizar(self):
        return self.supermercado


class BuilderBase:
    def __init__(self, dsl):
        self.dsl = dsl
        self._guardado = False

    def _guardar(self):
        raise NotImplementedError

    def producto(self, codigo):
        self._guardar()
        return self.dsl.producto(codigo)

    def promocion(self, codigo):
        self._guardar()
        return self.dsl.promocion(codigo)

    def finalizar(self):
        self._guardar()
        return self.dsl.finalizar()


class ProductoBuilder(BuilderBase):
    def __init__(self, dsl, codigo):
        super().__init__(dsl)
        self.codigo = codigo
        self._nombre = None
        self._precio = None
        self._categoria = None

    def nombre(self, nombre):
        self._nombre = nombre
        return self

    def precio(self, precio):
        self._precio = precio
        return self

    def categoria(self, categoria):
        self._categoria = categoria
        return self

    def _guardar(self):
        if self._guardado:
            return
        producto = Producto(
            self.codigo,
            self._nombre,
            self._precio,
            self._categoria,
        )
        self.dsl.supermercado.agregar_producto(producto)
        self._guardado = True


class PromocionBuilder(BuilderBase):
    def __init__(self, dsl, codigo):
        super().__init__(dsl)
        self.codigo = codigo
        self._nombre = None
        self._descuento = None
        self._condiciones = []

    def nombre(self, nombre):
        self._nombre = nombre
        return self

    def descuento(self, porcentaje):
        self._descuento = porcentaje
        return self

    def cuando_producto(self, codigo):
        return CondicionBuilder(self, codigo)

    def _agregar_condicion(self, condicion):
        self._condiciones.append(condicion)

    def _guardar(self):
        if self._guardado:
            return
        promocion = Promocion(
            self.codigo,
            self._nombre,
            self._descuento,
            self._condiciones,
        )
        self.dsl.supermercado.agregar_promocion(promocion)
        self._guardado = True


class CondicionBuilder:
    def __init__(self, promocion_builder, codigo_producto):
        self.promocion_builder = promocion_builder
        self.codigo_producto = codigo_producto
        self._guardada = False

    def _guardar(self, operador="=", cantidad=1):
        if not self._guardada:
            condicion = Condicion(
                self.codigo_producto,
                operador,
                cantidad,
            )
            self.promocion_builder._agregar_condicion(condicion)
            self._guardada = True
        return self.promocion_builder

    def cantidad_igual(self, cantidad):
        return self._guardar("=", cantidad)

    def cantidad_mayor_igual(self, cantidad):
        return self._guardar(">=", cantidad)

    def nombre(self, nombre):
        return self._guardar().nombre(nombre)

    def descuento(self, porcentaje):
        return self._guardar().descuento(porcentaje)

    def cuando_producto(self, codigo):
        return self._guardar().cuando_producto(codigo)

    def producto(self, codigo):
        return self._guardar().producto(codigo)

    def promocion(self, codigo):
        return self._guardar().promocion(codigo)

    def finalizar(self):
        return self._guardar().finalizar()
