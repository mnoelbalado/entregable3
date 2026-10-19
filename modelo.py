
class Producto:
    def __init__(self, codigo, nombre, precio, categoria=None):
        self.codigo = codigo
        self.nombre = nombre
        self.precio = precio
        self.categoria = categoria


class Condicion:
    def __init__(self, codigo_producto, operador="=", cantidad=1):
        self.codigo_producto = codigo_producto
        self.operador = operador
        self.cantidad = cantidad


class Promocion:
    def __init__(self, codigo, nombre, descuento, condiciones):
        self.codigo = codigo
        self.nombre = nombre
        self.descuento = descuento
        self.condiciones = condiciones


class LineaCompra:
    def __init__(self, codigo_producto, precio, cantidad,
                 descuento=0):
        self.codigo_producto = codigo_producto
        self.precio = precio
        self.cantidad = cantidad
        self.descuento = descuento

    def calcular_importe(self):
        subtotal = self.precio * self.cantidad
        return subtotal * (1 - self.descuento / 100)


class Compra:
    def __init__(self):
        self.lineas = []
        self.promociones_aplicadas = []

    def calcular_total(self):
        return sum(linea.calcular_importe()
                   for linea in self.lineas)
