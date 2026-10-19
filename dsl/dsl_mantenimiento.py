from dataclasses import dataclass
from pathlib import Path

from lark import Lark, Transformer, UnexpectedInput

from modelo import Condicion, Producto, Promocion


GRAMATICA = r"""
    start: operacion*

    ?operacion: agregar_producto
              | actualizar_producto
              | eliminar_producto
              | agregar_promocion
              | actualizar_promocion
              | eliminar_promocion

    agregar_producto: "AGREGAR" "PRODUCTO" ENTERO atributo_producto* "FIN"
    actualizar_producto: "ACTUALIZAR" "PRODUCTO" ENTERO atributo_producto* "FIN"
    eliminar_producto: "ELIMINAR" "PRODUCTO" ENTERO

    agregar_promocion: "AGREGAR" "PROMOCION" ENTERO atributo_promocion* "FIN"
    actualizar_promocion: "ACTUALIZAR" "PROMOCION" ENTERO atributo_promocion* "FIN"
    eliminar_promocion: "ELIMINAR" "PROMOCION" ENTERO

    ?atributo_producto: "NOMBRE" TEXTO       -> nombre
                      | "PRECIO" NUMERO      -> precio
                      | "CATEGORIA" TEXTO    -> categoria

    ?atributo_promocion: "NOMBRE" TEXTO      -> nombre
                       | "DESCUENTO" NUMERO  -> descuento
                       | cuando

    cuando: "CUANDO" condicion+
    ?condicion: "PRODUCTO" ENTERO "CANTIDAD" OPERADOR ENTERO -> condicion_cantidad
              | "PRODUCTO" ENTERO                            -> condicion_default

    OPERADOR: ">=" | "="
    TEXTO: /"[^"\r\n]*"/ | /“[^”\r\n]*”/
    NUMERO: /[+-]?(?:\d+\.\d+|\d+)/
    ENTERO: /[+-]?\d+/

    %import common.WS
    %ignore WS
"""


@dataclass(frozen=True)
class Operacion:
    accion: str
    entidad: str
    codigo: int
    atributos: tuple = ()


class TransformadorMantenimiento(Transformer):
    def start(self, operaciones):
        return list(operaciones)

    def nombre(self, elementos):
        return "nombre", self._texto(elementos[0])

    def precio(self, elementos):
        return "precio", self._numero(elementos[0])

    def categoria(self, elementos):
        return "categoria", self._texto(elementos[0])

    def descuento(self, elementos):
        return "descuento", self._numero(elementos[0])

    def condicion_default(self, elementos):
        return int(elementos[0]), "=", 1

    def condicion_cantidad(self, elementos):
        codigo, operador, cantidad = elementos
        return int(codigo), str(operador), int(cantidad)

    def cuando(self, condiciones):
        return "condiciones", list(condiciones)

    def agregar_producto(self, elementos):
        return self._operacion("agregar", "producto", elementos)

    def actualizar_producto(self, elementos):
        return self._operacion("actualizar", "producto", elementos)

    def eliminar_producto(self, elementos):
        return Operacion("eliminar", "producto", int(elementos[0]))

    def agregar_promocion(self, elementos):
        return self._operacion("agregar", "promocion", elementos)

    def actualizar_promocion(self, elementos):
        return self._operacion("actualizar", "promocion", elementos)

    def eliminar_promocion(self, elementos):
        return Operacion("eliminar", "promocion", int(elementos[0]))

    @staticmethod
    def _operacion(accion, entidad, elementos):
        codigo, *atributos = elementos
        return Operacion(accion, entidad, int(codigo), tuple(atributos))

    @staticmethod
    def _texto(token):
        return str(token)[1:-1]

    @staticmethod
    def _numero(token):
        texto = str(token)
        return float(texto) if "." in texto else int(texto)


class DSLMantenimiento:
    def __init__(self, supermercado):
        self.supermercado = supermercado
        self.errores = []
        self._parser = Lark(GRAMATICA, parser="lalr")
        self._transformador = TransformadorMantenimiento()

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

        operaciones = self._transformador.transform(arbol)
        for numero, operacion in enumerate(operaciones, start=1):
            try:
                self._ejecutar(operacion)
            except ValueError as error:
                self.errores.append(
                    f"Operacion {numero} "
                    f"({operacion.accion} {operacion.entidad} "
                    f"{operacion.codigo}): {error}"
                )
        return list(self.errores)

    def procesar_archivo(self, ruta, encoding="utf-8"):
        texto = Path(ruta).read_text(encoding=encoding)
        return self.procesar(texto)

    def _ejecutar(self, operacion):
        atributos = self._atributos(operacion.atributos)
        metodo = getattr(
            self,
            f"_{operacion.accion}_{operacion.entidad}",
        )
        metodo(operacion.codigo, atributos)

    @staticmethod
    def _atributos(pares):
        atributos = {}
        for nombre, valor in pares:
            if nombre in atributos:
                raise ValueError(f"El atributo {nombre} esta repetido")
            atributos[nombre] = valor
        return atributos

    def _agregar_producto(self, codigo, atributos):
        producto = Producto(
            codigo,
            atributos.get("nombre"),
            atributos.get("precio"),
            atributos.get("categoria"),
        )
        self.supermercado.agregar_producto(producto)

    def _actualizar_producto(self, codigo, atributos):
        self.supermercado.actualizar_producto(codigo, **atributos)

    def _eliminar_producto(self, codigo, _atributos):
        self.supermercado.eliminar_producto(codigo)

    def _agregar_promocion(self, codigo, atributos):
        condiciones = self._crear_condiciones(
            atributos.get("condiciones", [])
        )
        promocion = Promocion(
            codigo,
            atributos.get("nombre"),
            atributos.get("descuento"),
            condiciones,
        )
        self.supermercado.agregar_promocion(promocion)

    def _actualizar_promocion(self, codigo, atributos):
        if "condiciones" in atributos:
            atributos["condiciones"] = self._crear_condiciones(
                atributos["condiciones"]
            )
        self.supermercado.actualizar_promocion(codigo, **atributos)

    def _eliminar_promocion(self, codigo, _atributos):
        self.supermercado.eliminar_promocion(codigo)

    @staticmethod
    def _crear_condiciones(datos):
        return [
            Condicion(codigo, operador, cantidad)
            for codigo, operador, cantidad in datos
        ]
