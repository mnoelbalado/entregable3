from decimal import Decimal, InvalidOperation


def validar_entero(valor, campo, positivo=False):
    if isinstance(valor, bool) or not isinstance(valor, int):
        raise ValueError(f"{campo} debe ser un numero entero")
    if positivo and valor <= 0:
        raise ValueError(f"{campo} debe ser mayor que cero")
    return valor


def validar_texto(valor, campo, permite_vacio=False):
    if not isinstance(valor, str):
        raise ValueError(f"{campo} debe ser texto")
    if not permite_vacio and not valor.strip():
        raise ValueError(f"{campo} es obligatorio")
    return valor


def validar_numero(
    valor,
    campo,
    minimo=None,
    maximo=None,
    maximo_decimales=2,
):
    if isinstance(valor, bool) or not isinstance(valor, (int, float, Decimal)):
        raise ValueError(f"{campo} debe ser un numero")

    try:
        decimal = Decimal(str(valor))
    except InvalidOperation as error:
        raise ValueError(f"{campo} debe ser un numero") from error

    if not decimal.is_finite():
        raise ValueError(f"{campo} debe ser un numero finito")
    decimales = max(0, -decimal.as_tuple().exponent)
    if maximo_decimales is not None and decimales > maximo_decimales:
        raise ValueError(
            f"{campo} admite hasta {maximo_decimales} decimales"
        )
    if minimo is not None and decimal < Decimal(str(minimo)):
        raise ValueError(f"{campo} debe ser mayor o igual a {minimo}")
    if maximo is not None and decimal > Decimal(str(maximo)):
        raise ValueError(f"{campo} debe ser menor o igual a {maximo}")
    return float(decimal) if decimales else int(decimal)


class Producto:
    def __init__(self, codigo, nombre, precio, categoria=None):
        self.codigo = validar_entero(codigo, "El codigo del producto")
        self.nombre = validar_texto(nombre, "El nombre del producto")
        self.precio = validar_numero(
            precio, "El precio del producto", minimo=0
        )
        if categoria is not None:
            validar_texto(
                categoria, "La categoria del producto", permite_vacio=True
            )
        self.categoria = categoria


class Condicion:
    OPERADORES = {"=", ">="}

    def __init__(self, codigo_producto, operador="=", cantidad=1):
        self.codigo_producto = validar_entero(
            codigo_producto, "El codigo del producto"
        )
        if operador not in self.OPERADORES:
            raise ValueError("El operador debe ser '=' o '>='")
        self.operador = operador
        self.cantidad = validar_entero(
            cantidad, "La cantidad de la condicion", positivo=True
        )


class Promocion:
    def __init__(self, codigo, nombre, descuento, condiciones):
        self.codigo = validar_entero(codigo, "El codigo de la promocion")
        self.nombre = validar_texto(nombre, "El nombre de la promocion")
        self.descuento = validar_numero(
            descuento,
            "El descuento de la promocion",
            minimo=0,
            maximo=100,
            maximo_decimales=None,
        )

        self.condiciones = list(condiciones or [])
        if not self.condiciones:
            raise ValueError("La promocion debe tener al menos una condicion")
        if not all(isinstance(condicion, Condicion)
                   for condicion in self.condiciones):
            raise ValueError("Las condiciones de la promocion no son validas")

        codigos = [condicion.codigo_producto
                   for condicion in self.condiciones]
        if len(codigos) != len(set(codigos)):
            raise ValueError(
                "La promocion no puede repetir un producto en sus condiciones"
            )


class LineaCompra:
    def __init__(self, codigo_producto, precio, cantidad, descuento=0):
        self.codigo_producto = validar_entero(
            codigo_producto, "El codigo del producto"
        )
        self.precio = validar_numero(precio, "El precio", minimo=0)
        self.cantidad = validar_entero(
            cantidad, "La cantidad comprada", positivo=True
        )
        self.descuento = validar_numero(
            descuento,
            "El descuento",
            minimo=0,
            maximo=100,
            maximo_decimales=None,
        )

    def calcular_importe(self):
        subtotal = self.precio * self.cantidad
        return subtotal * (1 - self.descuento / 100)

    @property
    def importe(self):
        return self.calcular_importe()


class Compra:
    def __init__(self, lineas=None, promociones_aplicadas=None):
        self.lineas = list(lineas or [])
        self.promociones_aplicadas = list(promociones_aplicadas or [])

        if not all(isinstance(linea, LineaCompra) for linea in self.lineas):
            raise ValueError("Las lineas de la compra no son validas")
        if not self.lineas:
            raise ValueError("La compra debe tener al menos un producto")
        if not all(isinstance(promocion, Promocion)
                   for promocion in self.promociones_aplicadas):
            raise ValueError("Las promociones aplicadas no son validas")

    def calcular_total(self):
        return sum(linea.calcular_importe() for linea in self.lineas)

    @property
    def importe_total(self):
        return self.calcular_total()
