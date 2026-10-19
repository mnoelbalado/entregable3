
from supermercado import Supermercado
from dsl.dsl_interno import DSLSupermercado


def cargar_datos_iniciales(supermercado):
    DSLSupermercado(supermercado) \
        .producto(1) \
            .nombre("Arroz") \
            .precio(50) \
            .categoria("Comestible") \
        .producto(2) \
            .nombre("Harina") \
            .precio(30) \
        .promocion(1) \
            .nombre("Harina x5") \
            .cuando_producto(2) \
                .cantidad_mayor_igual(5) \
            .descuento(20) \
        .finalizar()


def main():
    supermercado = Supermercado()
    cargar_datos_iniciales(supermercado)

    print("Productos cargados:")
    for producto in supermercado.productos.values():
        print(
            producto.codigo,
            producto.nombre,
            producto.precio,
            producto.categoria
        )

    print("\nPromociones cargadas:")
    for promocion in supermercado.promociones.values():
        print(
            promocion.codigo,
            promocion.nombre,
            promocion.descuento
        )


if __name__ == "__main__":
    main()
