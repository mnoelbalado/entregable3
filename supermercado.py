
class Supermercado:
    def __init__(self):
        self.productos = {}
        self.promociones = {}
        self.compras = []

    def agregar_producto(self, producto):
        if producto.codigo in self.productos:
            raise ValueError(
                f"Ya existe el producto {producto.codigo}"
            )

        self.productos[producto.codigo] = producto

    def obtener_producto(self, codigo):
        if codigo not in self.productos:
            raise ValueError(
                f"No existe el producto {codigo}"
            )

        return self.productos[codigo]

    def agregar_promocion(self, promocion):
        if promocion.codigo in self.promociones:
            raise ValueError(
                f"Ya existe la promoción {promocion.codigo}"
            )

        for condicion in promocion.condiciones:
            self.obtener_producto(condicion.codigo_producto)

        self.promociones[promocion.codigo] = promocion
