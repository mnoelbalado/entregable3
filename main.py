from dsl.dsl_compras import DSLCompras
from dsl.dsl_interno import DSLSupermercado
from dsl.dsl_mantenimiento import DSLMantenimiento
from supermercado import Supermercado


def cargar_datos_iniciales(supermercado):
    return (
        DSLSupermercado(supermercado)
        .producto(1)
            .nombre("Arroz")
            .precio(50)
            .categoria("Comestible")
        .producto(2)
            .nombre("Harina")
            .precio(30)
        .producto(3)
            .categoria("Bebida")
            .precio(100)
            .nombre("Refresco")
        .promocion(1)
            .nombre("Harina x5")
            .cuando_producto(2)
                .cantidad_mayor_igual(5)
            .descuento(20)
        .producto(4)
            .precio(150)
            .nombre("Pizza")
        .promocion(2)
            .descuento(25)
            .cuando_producto(3)
            .cuando_producto(4)
                .cantidad_igual(2)
            .nombre("2 pizzas + refresco")
        .finalizar()
    )


def mostrar_productos(supermercado, salida=print):
    productos = supermercado.listar_productos()
    if not productos:
        salida("No hay productos cargados.")
        return

    salida("\nProductos:")
    for producto in productos:
        categoria = producto.categoria or "Sin categoria"
        salida(
            f"Codigo: {producto.codigo} | Nombre: {producto.nombre} | "
            f"Precio: {producto.precio} | Categoria: {categoria}"
        )


def mostrar_promociones(supermercado, salida=print):
    promociones = supermercado.listar_promociones()
    if not promociones:
        salida("No hay promociones cargadas.")
        return

    salida("\nPromociones:")
    for promocion in promociones:
        salida(
            f"Codigo: {promocion.codigo} | Nombre: {promocion.nombre} | "
            f"Descuento: {promocion.descuento}%"
        )
        for condicion in promocion.condiciones:
            producto = supermercado.obtener_producto(
                condicion.codigo_producto
            )
            salida(
                f"  Producto {producto.codigo} - {producto.nombre} | "
                f"Cantidad {condicion.operador} {condicion.cantidad}"
            )


def mostrar_compras(supermercado, salida=print):
    compras = supermercado.listar_compras()
    if not compras:
        salida("No hay compras registradas.")
        return

    salida("\nCompras:")
    for numero, compra in enumerate(compras, start=1):
        salida(f"Compra {numero}:")
        for linea in compra.lineas:
            nombre = linea.nombre_producto or "Producto no disponible"
            salida(
                f"  Producto {linea.codigo_producto} - {nombre} | "
                f"Cantidad: {linea.cantidad} | "
                f"Precio unitario: {linea.precio} | "
                f"Descuento: {linea.descuento}% | "
                f"Importe: {linea.importe}"
            )

        if compra.promociones_aplicadas:
            salida("  Promociones aplicadas:")
            for promocion in compra.promociones_aplicadas:
                salida(f"    {promocion.codigo} - {promocion.nombre}")
        else:
            salida("  Promociones aplicadas: ninguna")
        salida(f"  Importe total: {compra.importe_total}")


def procesar_archivo(dsl, ruta, salida=print):
    try:
        errores = dsl.procesar_archivo(ruta)
    except OSError as error:
        salida(f"No se pudo leer el archivo: {error}")
        return False

    if errores:
        salida("Se encontraron errores:")
        for error in errores:
            salida(f"  - {error}")
        return False

    salida("Archivo procesado correctamente.")
    return True


def realizar_compra_interactiva(supermercado, entrada=input, salida=print):
    mostrar_productos(supermercado, salida)
    if not supermercado.listar_productos():
        salida("No hay productos disponibles para realizar una compra.")
        return False

    productos_seleccionados = []
    salida("\nIngrese FIN como codigo para finalizar la compra.")

    while True:
        codigo_ingresado = entrada("Codigo del producto: ").strip()
        if codigo_ingresado.upper() == "FIN":
            break

        try:
            codigo = int(codigo_ingresado)
        except ValueError:
            salida("Error: el codigo debe ser un numero entero.")
            continue

        try:
            producto = supermercado.obtener_producto(codigo)
        except ValueError as error:
            salida(f"Error: {error}")
            continue

        cantidad_ingresada = entrada(
            f"Cantidad de {producto.nombre}: "
        ).strip()
        try:
            cantidad = int(cantidad_ingresada)
        except ValueError:
            salida("Error: la cantidad debe ser un numero entero positivo.")
            continue

        if cantidad <= 0:
            salida("Error: la cantidad debe ser un numero entero positivo.")
            continue

        productos_seleccionados.append((codigo, cantidad))
        salida(f"Agregado: {cantidad} x {producto.nombre}")

    if not productos_seleccionados:
        salida("Compra cancelada: no se seleccionaron productos.")
        return False

    texto_compra = "\n".join(
        ["COMPRA"]
        + [
            f"PRODUCTO {codigo} CANTIDAD {cantidad}"
            for codigo, cantidad in productos_seleccionados
        ]
        + ["FIN"]
    )
    errores = DSLCompras(supermercado).procesar(texto_compra)

    if errores:
        salida("No se pudo realizar la compra:")
        for error in errores:
            salida(f"  - {error}")
        return False

    compra = supermercado.compras[-1]
    salida("Compra realizada correctamente.")
    salida(f"Importe total: {compra.importe_total}")
    return True


def mostrar_menu(salida=print):
    salida("\nMenu principal")
    salida("1. Mantenimiento de productos y promociones")
    salida("2. Realizar compras")
    salida("3. Ver la lista de productos")
    salida("4. Ver la lista de promociones")
    salida("5. Ver la lista de compras")
    salida("6. Realizar una compra interactiva")
    salida("0. Salir")


def ejecutar_menu(supermercado, entrada=input, salida=print):
    dsl_mantenimiento = DSLMantenimiento(supermercado)
    dsl_compras = DSLCompras(supermercado)

    while True:
        mostrar_menu(salida)
        opcion = entrada("Seleccione una opcion: ").strip()

        if opcion == "0":
            salida("Programa finalizado.")
            return
        if opcion == "1":
            ruta = entrada("Archivo de mantenimiento: ").strip()
            procesar_archivo(dsl_mantenimiento, ruta, salida)
        elif opcion == "2":
            ruta = entrada("Archivo de compras: ").strip()
            procesar_archivo(dsl_compras, ruta, salida)
        elif opcion == "3":
            mostrar_productos(supermercado, salida)
        elif opcion == "4":
            mostrar_promociones(supermercado, salida)
        elif opcion == "5":
            mostrar_compras(supermercado, salida)
        elif opcion == "6":
            if entrada is input and salida is print:
                try:
                    from compra_ui import abrir_pantalla_compra

                    if not supermercado.listar_productos():
                        salida(
                            "No hay productos disponibles para realizar "
                            "una compra."
                        )
                    else:
                        abrir_pantalla_compra(supermercado)
                except (ImportError, RuntimeError) as error:
                    salida(
                        "No se pudo abrir la pantalla de compra "
                        f"({error}). Se usara el modo consola."
                    )
                    realizar_compra_interactiva(
                        supermercado, entrada, salida
                    )
            else:
                realizar_compra_interactiva(supermercado, entrada, salida)
        else:
            salida("Opcion invalida.")


def main():
    supermercado = cargar_datos_iniciales(Supermercado())
    ejecutar_menu(supermercado)


if __name__ == "__main__":
    main()
