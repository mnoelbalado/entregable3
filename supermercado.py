from collections import defaultdict

from modelo import (
    Compra,
    LineaCompra,
    Producto,
    Promocion,
    validar_entero,
)


NO_ESPECIFICADO = object()


class Supermercado:
    def __init__(self):
        self.productos = {}
        self.promociones = {}
        self.compras = []

    def agregar_producto(self, producto):
        if not isinstance(producto, Producto):
            raise ValueError("El producto no es valido")
        if producto.codigo in self.productos:
            raise ValueError(f"Ya existe el producto {producto.codigo}")

        self.productos[producto.codigo] = producto
        return producto

    def obtener_producto(self, codigo):
        validar_entero(codigo, "El codigo del producto")
        if codigo not in self.productos:
            raise ValueError(f"No existe el producto {codigo}")

        return self.productos[codigo]

    def actualizar_producto(
        self,
        codigo,
        nombre=NO_ESPECIFICADO,
        precio=NO_ESPECIFICADO,
        categoria=NO_ESPECIFICADO,
    ):
        actual = self.obtener_producto(codigo)
        actualizado = Producto(
            codigo,
            actual.nombre if nombre is NO_ESPECIFICADO else nombre,
            actual.precio if precio is NO_ESPECIFICADO else precio,
            actual.categoria if categoria is NO_ESPECIFICADO else categoria,
        )
        self.productos[codigo] = actualizado
        return actualizado

    def eliminar_producto(self, codigo):
        producto = self.obtener_producto(codigo)
        for promocion in self.promociones.values():
            if any(condicion.codigo_producto == codigo
                   for condicion in promocion.condiciones):
                raise ValueError(
                    f"No se puede eliminar el producto {codigo}: "
                    f"esta asociado a la promocion {promocion.codigo}"
                )

        del self.productos[codigo]
        return producto

    def listar_productos(self):
        return list(self.productos.values())

    def agregar_promocion(self, promocion):
        if not isinstance(promocion, Promocion):
            raise ValueError("La promocion no es valida")
        if promocion.codigo in self.promociones:
            raise ValueError(f"Ya existe la promocion {promocion.codigo}")

        self._validar_productos_de_promocion(promocion)
        self.promociones[promocion.codigo] = promocion
        return promocion

    def obtener_promocion(self, codigo):
        validar_entero(codigo, "El codigo de la promocion")
        if codigo not in self.promociones:
            raise ValueError(f"No existe la promocion {codigo}")
        return self.promociones[codigo]

    def actualizar_promocion(
        self,
        codigo,
        nombre=NO_ESPECIFICADO,
        descuento=NO_ESPECIFICADO,
        condiciones=NO_ESPECIFICADO,
    ):
        actual = self.obtener_promocion(codigo)
        actualizada = Promocion(
            codigo,
            actual.nombre if nombre is NO_ESPECIFICADO else nombre,
            actual.descuento
            if descuento is NO_ESPECIFICADO else descuento,
            actual.condiciones
            if condiciones is NO_ESPECIFICADO else condiciones,
        )
        self._validar_productos_de_promocion(actualizada)
        self.promociones[codigo] = actualizada
        return actualizada

    def eliminar_promocion(self, codigo):
        promocion = self.obtener_promocion(codigo)
        del self.promociones[codigo]
        return promocion

    def listar_promociones(self):
        return list(self.promociones.values())

    def realizar_compra(self, productos_cantidades):
        cantidades = self._normalizar_compra(productos_cantidades)
        restantes = cantidades.copy()
        cantidades_con_descuento = defaultdict(int)
        promociones_aplicadas = []

        promociones = sorted(
            self.promociones.values(),
            key=lambda promocion: (-promocion.descuento, promocion.codigo),
        )
        for promocion in promociones:
            aplicaciones = 0
            while self._puede_aplicarse(promocion, restantes):
                for condicion in promocion.condiciones:
                    restantes[condicion.codigo_producto] -= condicion.cantidad
                    clave = (condicion.codigo_producto, promocion.descuento)
                    cantidades_con_descuento[clave] += condicion.cantidad
                aplicaciones += 1
            if aplicaciones:
                promociones_aplicadas.append(promocion)

        lineas = []
        for codigo in cantidades:
            producto = self.productos[codigo]
            descuentos = sorted(
                (
                    (descuento, cantidad)
                    for (codigo_con_descuento, descuento), cantidad
                    in cantidades_con_descuento.items()
                    if codigo_con_descuento == codigo
                ),
                reverse=True,
            )
            for descuento, cantidad in descuentos:
                lineas.append(
                    LineaCompra(codigo, producto.precio, cantidad, descuento)
                )
            if restantes[codigo]:
                lineas.append(
                    LineaCompra(codigo, producto.precio, restantes[codigo])
                )

        compra = Compra(lineas, promociones_aplicadas)
        self.compras.append(compra)
        return compra

    def listar_compras(self):
        return list(self.compras)

    def _validar_productos_de_promocion(self, promocion):
        for condicion in promocion.condiciones:
            self.obtener_producto(condicion.codigo_producto)

    def _normalizar_compra(self, productos_cantidades):
        items = (
            productos_cantidades.items()
            if isinstance(productos_cantidades, dict)
            else productos_cantidades
        )
        if items is None:
            raise ValueError("La compra debe tener al menos un producto")

        cantidades = {}
        try:
            for codigo, cantidad in items:
                validar_entero(codigo, "El codigo del producto")
                validar_entero(cantidad, "La cantidad comprada", positivo=True)
                self.obtener_producto(codigo)
                cantidades[codigo] = cantidades.get(codigo, 0) + cantidad
        except (TypeError, ValueError) as error:
            if isinstance(error, ValueError):
                raise
            raise ValueError(
                "La compra debe contener pares de codigo y cantidad"
            ) from error

        if not cantidades:
            raise ValueError("La compra debe tener al menos un producto")
        return cantidades

    @staticmethod
    def _puede_aplicarse(promocion, cantidades_disponibles):
        # Las cantidades representan unidades consumidas por cada aplicacion.
        # Esto permite, como exige la letra, aplicar dos veces una condicion de
        # cuatro unidades cuando se compran ocho, sin que las sobrantes anulen
        # una aplicacion. El operador se conserva para el DSL y los listados.
        return all(
            cantidades_disponibles.get(condicion.codigo_producto, 0)
            >= condicion.cantidad
            for condicion in promocion.condiciones
        )
