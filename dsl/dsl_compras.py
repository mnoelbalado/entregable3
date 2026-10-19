from pathlib import Path

from lark import Lark, Transformer, UnexpectedInput


GRAMATICA = r"""
    start: compra*
    compra: "COMPRA" linea* "FIN"

    ?linea: "PRODUCTO" ENTERO "CANTIDAD" ENTERO -> producto_cantidad
          | "PRODUCTO" ENTERO                    -> producto_default

    ENTERO: /[+-]?\d+/

    %import common.WS
    %ignore WS
"""


class TransformadorCompras(Transformer):
    def start(self, compras):
        return list(compras)

    def producto_default(self, elementos):
        return int(elementos[0]), 1

    def producto_cantidad(self, elementos):
        codigo, cantidad = elementos
        return int(codigo), int(cantidad)

    def compra(self, lineas):
        return list(lineas)


class DSLCompras:
    def __init__(self, supermercado):
        self.supermercado = supermercado
        self.errores = []
        self._parser = Lark(GRAMATICA, parser="lalr")
        self._transformador = TransformadorCompras()

    def procesar(self, texto):
        self.errores = []
        try:
            arbol = self._parser.parse(texto)
        except UnexpectedInput as error:
            contexto = error.get_context(texto).strip()
            self.errores.append(
                f"Error sintactico en linea {error.line}, "
                f"columna {error.column}: {contexto}"
            )
            return list(self.errores)

        compras = self._transformador.transform(arbol)
        for numero, productos_cantidades in enumerate(compras, start=1):
            try:
                self.supermercado.realizar_compra(productos_cantidades)
            except ValueError as error:
                self.errores.append(f"Compra {numero}: {error}")
        return list(self.errores)

    def procesar_archivo(self, ruta, encoding="utf-8"):
        texto = Path(ruta).read_text(encoding=encoding)
        return self.procesar(texto)
