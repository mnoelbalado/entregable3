"""Interfaz grafica sencilla para registrar una compra."""

from copy import deepcopy
import tkinter as tk
from tkinter import messagebox, ttk

from dsl.dsl_compras import DSLCompras


class PantallaCompra:
    COLOR_FONDO = "#f4f6f8"
    COLOR_PRIMARIO = "#176b5b"
    COLOR_PRIMARIO_ACTIVO = "#0f5447"
    COLOR_PROMOCION = "#dff3e8"
    COLOR_FILA_ALTERNA = "#f1f7f5"
    COLOR_AVISO = "#9a5b00"

    def __init__(self, supermercado):
        self.supermercado = supermercado
        self.cantidades = {}
        self.compra_realizada = False

        self.ventana = tk.Tk()
        self.ventana.title("Supermercado - Nueva compra")
        self.ventana.geometry("1080x680")
        self.ventana.minsize(920, 600)
        self.ventana.configure(background=self.COLOR_FONDO)

        self.cantidad = tk.StringVar(value="1")
        self.subtotal = tk.StringVar(value="$ 0.00")
        self.descuento = tk.StringVar(value="- $ 0.00")
        self.total = tk.StringVar(value="$ 0.00")
        self.promociones_aplicables = tk.StringVar(value="Ninguna")
        self.aviso_promocion = tk.StringVar()
        self.estado = tk.StringVar(
            value="Seleccione un producto para comenzar la compra."
        )

        self._configurar_estilos()
        self._crear_contenido()
        self._cargar_productos()
        self._cargar_promociones()
        self._actualizar_carrito()

    def _configurar_estilos(self):
        estilo = ttk.Style(self.ventana)
        estilo.theme_use("clam")
        estilo.configure("TFrame", background=self.COLOR_FONDO)
        estilo.configure("TLabel", background=self.COLOR_FONDO)
        estilo.configure("Titulo.TLabel", font=("Segoe UI", 20, "bold"))
        estilo.configure("Seccion.TLabel", font=("Segoe UI", 12, "bold"))
        estilo.configure(
            "Ayuda.TLabel",
            foreground="#53625f",
            font=("Segoe UI", 10),
        )
        estilo.configure(
            "Aviso.TLabel",
            foreground=self.COLOR_AVISO,
            font=("Segoe UI", 10, "bold"),
        )
        estilo.configure(
            "Estado.TLabel",
            foreground="#42504d",
            font=("Segoe UI", 10),
        )
        estilo.configure(
            "Total.TLabel",
            font=("Segoe UI", 17, "bold"),
            foreground=self.COLOR_PRIMARIO,
            background=self.COLOR_FONDO,
        )
        estilo.configure(
            "Resumen.TLabelframe",
            background=self.COLOR_FONDO,
            bordercolor="#bcc8c5",
            relief="solid",
        )
        estilo.configure(
            "Resumen.TLabelframe.Label",
            background=self.COLOR_FONDO,
            foreground="#34413e",
            font=("Segoe UI", 10, "bold"),
        )
        estilo.configure(
            "Resumen.TLabel",
            background=self.COLOR_FONDO,
            foreground="#253330",
        )
        estilo.configure(
            "ResumenPromocion.TLabel",
            background=self.COLOR_FONDO,
            foreground=self.COLOR_PRIMARIO,
        )
        estilo.configure("Accion.TButton", font=("Segoe UI", 10, "bold"))
        estilo.configure(
            "Primario.TButton",
            background=self.COLOR_PRIMARIO,
            foreground="white",
            font=("Segoe UI", 10, "bold"),
            padding=(14, 8),
        )
        estilo.map(
            "Primario.TButton",
            background=[
                ("active", self.COLOR_PRIMARIO_ACTIVO),
                ("disabled", "#a9b6b3"),
            ],
        )
        estilo.configure(
            "Treeview", rowheight=28, font=("Segoe UI", 10)
        )
        estilo.configure(
            "Treeview.Heading", font=("Segoe UI", 10, "bold")
        )

    def _crear_contenido(self):
        contenedor = ttk.Frame(self.ventana, padding=18)
        contenedor.pack(fill="both", expand=True)
        contenedor.columnconfigure(0, weight=3)
        contenedor.columnconfigure(1, weight=2)
        contenedor.rowconfigure(2, weight=1)

        ttk.Label(
            contenedor, text="Nueva compra", style="Titulo.TLabel"
        ).grid(row=0, column=0, columnspan=2, sticky="w")
        ttk.Label(
            contenedor,
            text="Seleccione productos y revise los descuentos antes de pagar.",
            style="Ayuda.TLabel",
        ).grid(row=1, column=0, columnspan=2, sticky="w", pady=(2, 14))

        izquierda = ttk.Frame(contenedor, padding=(0, 0, 9, 0))
        izquierda.grid(row=2, column=0, sticky="nsew")
        izquierda.columnconfigure(0, weight=1)
        izquierda.rowconfigure(1, weight=3)
        izquierda.rowconfigure(4, weight=2)

        derecha = ttk.Frame(contenedor, padding=(9, 0, 0, 0))
        derecha.grid(row=2, column=1, sticky="nsew")
        derecha.columnconfigure(0, weight=1)
        derecha.rowconfigure(1, weight=1)

        self._crear_catalogo(izquierda)
        self._crear_promociones(izquierda)
        self._crear_carrito(derecha)

        ttk.Separator(contenedor).grid(
            row=3, column=0, columnspan=2, sticky="ew", pady=(14, 10)
        )
        ttk.Label(
            contenedor, textvariable=self.estado, style="Estado.TLabel"
        ).grid(
            row=4, column=0, sticky="w"
        )

        botones = ttk.Frame(contenedor)
        botones.grid(row=4, column=1, sticky="e")
        ttk.Button(
            botones, text="Nueva compra", command=self._nueva_compra
        ).pack(side="left")
        ttk.Button(
            botones, text="Cerrar", command=self.ventana.destroy
        ).pack(side="left")
        self.boton_confirmar = ttk.Button(
            botones,
            text="Confirmar compra",
            command=self._confirmar_compra,
            style="Primario.TButton",
        )
        self.boton_confirmar.pack(side="left", padx=(8, 0))

    def _crear_catalogo(self, padre):
        ttk.Label(
            padre, text="Productos", style="Seccion.TLabel"
        ).grid(row=0, column=0, sticky="w", pady=(0, 6))

        self.tabla_productos = ttk.Treeview(
            padre,
            columns=("codigo", "nombre", "precio", "categoria"),
            show="headings",
            selectmode="browse",
        )
        self._configurar_columna(
            self.tabla_productos, "codigo", "Codigo", 65
        )
        self._configurar_columna(
            self.tabla_productos, "nombre", "Producto", 190
        )
        self._configurar_columna(
            self.tabla_productos, "precio", "Precio", 85
        )
        self._configurar_columna(
            self.tabla_productos, "categoria", "Categoria", 120
        )
        self.tabla_productos.grid(row=1, column=0, sticky="nsew")
        self.tabla_productos.tag_configure(
            "alterna", background=self.COLOR_FILA_ALTERNA
        )
        self.tabla_productos.bind(
            "<Double-1>", lambda _evento: self._agregar_producto()
        )
        self.tabla_productos.bind(
            "<Return>", lambda _evento: self._agregar_producto()
        )

        seleccion = ttk.Frame(padre)
        seleccion.grid(row=2, column=0, sticky="ew", pady=(8, 14))
        ttk.Label(seleccion, text="Cantidad:").pack(side="left")
        self.control_cantidad = ttk.Spinbox(
            seleccion,
            from_=1,
            to=999,
            width=6,
            textvariable=self.cantidad,
        )
        self.control_cantidad.pack(side="left", padx=(6, 10))
        ttk.Button(
            seleccion,
            text="Agregar al carrito",
            command=self._agregar_producto,
            style="Accion.TButton",
        ).pack(side="left")

    def _crear_promociones(self, padre):
        ttk.Label(
            padre, text="Promociones disponibles", style="Seccion.TLabel"
        ).grid(row=3, column=0, sticky="w", pady=(0, 6))

        self.tabla_promociones = ttk.Treeview(
            padre,
            columns=("nombre", "descuento", "condiciones"),
            show="headings",
            height=5,
            selectmode="none",
        )
        self._configurar_columna(
            self.tabla_promociones, "nombre", "Promocion", 160
        )
        self._configurar_columna(
            self.tabla_promociones, "descuento", "Dto.", 65
        )
        self._configurar_columna(
            self.tabla_promociones, "condiciones", "Como obtenerla", 250
        )
        self.tabla_promociones.tag_configure(
            "aplicada", background=self.COLOR_PROMOCION
        )
        self.tabla_promociones.grid(row=4, column=0, sticky="nsew")
        ttk.Label(
            padre,
            textvariable=self.aviso_promocion,
            style="Aviso.TLabel",
            wraplength=570,
        ).grid(row=5, column=0, sticky="ew", pady=(7, 0))

    def _crear_carrito(self, padre):
        ttk.Label(
            padre, text="Su carrito", style="Seccion.TLabel"
        ).grid(row=0, column=0, sticky="w", pady=(0, 6))

        self.tabla_carrito = ttk.Treeview(
            padre,
            columns=("nombre", "cantidad", "importe"),
            show="headings",
            selectmode="browse",
        )
        self._configurar_columna(
            self.tabla_carrito, "nombre", "Producto", 160
        )
        self._configurar_columna(
            self.tabla_carrito, "cantidad", "Cant.", 55
        )
        self._configurar_columna(
            self.tabla_carrito, "importe", "Importe", 85
        )
        self.tabla_carrito.grid(row=1, column=0, sticky="nsew")
        self.tabla_carrito.tag_configure(
            "alterna", background=self.COLOR_FILA_ALTERNA
        )

        controles = ttk.Frame(padre)
        controles.grid(row=2, column=0, sticky="ew", pady=8)
        ttk.Button(
            controles, text="−", width=3, command=self._restar_unidad
        ).pack(side="left")
        ttk.Button(
            controles, text="+", width=3, command=self._sumar_unidad
        ).pack(side="left", padx=5)
        ttk.Button(
            controles,
            text="Quitar",
            command=self._quitar_producto,
        ).pack(side="left")
        ttk.Button(
            controles,
            text="Vaciar",
            command=self._vaciar_carrito,
        ).pack(side="right")

        resumen = ttk.LabelFrame(
            padre,
            text="Resumen",
            padding=12,
            style="Resumen.TLabelframe",
        )
        resumen.grid(row=3, column=0, sticky="ew", pady=(8, 0))
        resumen.columnconfigure(1, weight=1)
        self._agregar_fila_resumen(resumen, 0, "Subtotal", self.subtotal)
        self._agregar_fila_resumen(resumen, 1, "Descuentos", self.descuento)
        ttk.Separator(resumen).grid(
            row=2, column=0, columnspan=2, sticky="ew", pady=8
        )
        ttk.Label(resumen, text="Total", style="Seccion.TLabel").grid(
            row=3, column=0, sticky="w"
        )
        ttk.Label(resumen, textvariable=self.total, style="Total.TLabel").grid(
            row=3, column=1, sticky="e"
        )
        ttk.Label(
            resumen,
            text="Promociones aplicadas:",
            style="Resumen.TLabel",
        ).grid(
            row=4, column=0, columnspan=2, sticky="w", pady=(12, 2)
        )
        ttk.Label(
            resumen,
            textvariable=self.promociones_aplicables,
            style="ResumenPromocion.TLabel",
            wraplength=320,
        ).grid(row=5, column=0, columnspan=2, sticky="w")

    @staticmethod
    def _agregar_fila_resumen(padre, fila, titulo, variable):
        ttk.Label(padre, text=titulo, style="Resumen.TLabel").grid(
            row=fila, column=0, sticky="w"
        )
        ttk.Label(
            padre, textvariable=variable, style="Resumen.TLabel"
        ).grid(
            row=fila, column=1, sticky="e"
        )

    @staticmethod
    def _configurar_columna(tabla, clave, titulo, ancho):
        tabla.heading(clave, text=titulo)
        tabla.column(clave, width=ancho, minwidth=50)

    def _cargar_productos(self):
        for indice, producto in enumerate(
            self.supermercado.listar_productos()
        ):
            self.tabla_productos.insert(
                "",
                "end",
                iid=str(producto.codigo),
                values=(
                    producto.codigo,
                    producto.nombre,
                    f"$ {producto.precio:.2f}",
                    producto.categoria or "Sin categoria",
                ),
                tags=("alterna",) if indice % 2 else (),
            )

    def _cargar_promociones(self):
        promociones = self.supermercado.listar_promociones()
        if not promociones:
            self.tabla_promociones.insert(
                "",
                "end",
                values=("No hay promociones vigentes", "-", "-"),
            )
            return

        for promocion in promociones:
            condiciones = []
            for condicion in promocion.condiciones:
                producto = self.supermercado.obtener_producto(
                    condicion.codigo_producto
                )
                cantidad = (
                    f"{condicion.cantidad} o mas"
                    if condicion.operador == ">="
                    else str(condicion.cantidad)
                )
                condiciones.append(f"{cantidad} x {producto.nombre}")

            self.tabla_promociones.insert(
                "",
                "end",
                iid=str(promocion.codigo),
                values=(
                    promocion.nombre,
                    f"{promocion.descuento}%",
                    " + ".join(condiciones),
                ),
            )

    def _agregar_producto(self):
        seleccion = self.tabla_productos.selection()
        if not seleccion:
            self.estado.set("Seleccione un producto de la lista.")
            return

        try:
            cantidad = int(self.cantidad.get())
            if cantidad <= 0:
                raise ValueError
        except ValueError:
            self.estado.set(
                "La cantidad debe ser un numero entero mayor que cero."
            )
            self.control_cantidad.focus_set()
            return

        codigo = int(seleccion[0])
        self.cantidades[codigo] = self.cantidades.get(codigo, 0) + cantidad
        producto = self.supermercado.obtener_producto(codigo)
        self.estado.set(f"Agregado: {cantidad} x {producto.nombre}")
        self.cantidad.set("1")
        self._actualizar_carrito(codigo)

    def _codigo_carrito_seleccionado(self):
        seleccion = self.tabla_carrito.selection()
        if not seleccion:
            self.estado.set("Seleccione un producto del carrito.")
            return None
        return int(seleccion[0])

    def _sumar_unidad(self):
        codigo = self._codigo_carrito_seleccionado()
        if codigo is not None:
            self.cantidades[codigo] += 1
            self._actualizar_carrito(codigo)

    def _restar_unidad(self):
        codigo = self._codigo_carrito_seleccionado()
        if codigo is None:
            return
        if self.cantidades[codigo] == 1:
            del self.cantidades[codigo]
            self._actualizar_carrito()
        else:
            self.cantidades[codigo] -= 1
            self._actualizar_carrito(codigo)

    def _quitar_producto(self):
        codigo = self._codigo_carrito_seleccionado()
        if codigo is not None:
            producto = self.supermercado.obtener_producto(codigo)
            del self.cantidades[codigo]
            self.estado.set(f"Se quito {producto.nombre} del carrito.")
            self._actualizar_carrito()

    def _vaciar_carrito(self):
        if not self.cantidades:
            return
        if messagebox.askyesno(
            "Vaciar carrito", "¿Desea quitar todos los productos?"
        ):
            self.cantidades.clear()
            self.estado.set("Carrito vacio.")
            self._actualizar_carrito()

    def _nueva_compra(self):
        if self.cantidades and not messagebox.askyesno(
            "Nueva compra",
            "La compra actual no fue confirmada. ¿Desea descartarla?",
        ):
            return
        self._reiniciar_compra(
            "Carrito listo. Puede comenzar una nueva compra."
        )

    def _reiniciar_compra(self, mensaje):
        self.cantidades.clear()
        self.cantidad.set("1")
        seleccion = self.tabla_productos.selection()
        if seleccion:
            self.tabla_productos.selection_remove(*seleccion)
        self._actualizar_carrito()
        self.estado.set(mensaje)

    def _actualizar_carrito(self, codigo_seleccionado=None):
        for item in self.tabla_carrito.get_children():
            self.tabla_carrito.delete(item)

        subtotal = 0
        for indice, (codigo, cantidad) in enumerate(self.cantidades.items()):
            producto = self.supermercado.obtener_producto(codigo)
            importe = producto.precio * cantidad
            subtotal += importe
            self.tabla_carrito.insert(
                "",
                "end",
                iid=str(codigo),
                values=(producto.nombre, cantidad, f"$ {importe:.2f}"),
                tags=("alterna",) if indice % 2 else (),
            )

        if codigo_seleccionado in self.cantidades:
            item = str(codigo_seleccionado)
            self.tabla_carrito.selection_set(item)
            self.tabla_carrito.focus(item)

        self._actualizar_resumen(subtotal)

    def _actualizar_resumen(self, subtotal):
        promociones = []
        total = subtotal
        if self.cantidades:
            copia = deepcopy(self.supermercado)
            compra = copia.realizar_compra(self.cantidades)
            total = compra.importe_total
            promociones = compra.promociones_aplicadas

        descuento = subtotal - total
        self.subtotal.set(f"$ {subtotal:.2f}")
        self.descuento.set(f"- $ {descuento:.2f}")
        self.total.set(f"$ {total:.2f}")
        self.promociones_aplicables.set(
            ", ".join(promocion.nombre for promocion in promociones)
            or "Ninguna"
        )
        self.boton_confirmar.configure(
            state="normal" if self.cantidades else "disabled"
        )

        codigos_aplicados = {promocion.codigo for promocion in promociones}
        for item in self.tabla_promociones.get_children():
            try:
                codigo = int(item)
            except ValueError:
                continue
            etiqueta = "aplicada" if codigo in codigos_aplicados else ""
            self.tabla_promociones.item(item, tags=(etiqueta,))

        self.aviso_promocion.set(
            self._crear_aviso_promocion(codigos_aplicados)
        )

        if promociones:
            self.estado.set(
                "Promocion aplicada. El total ya incluye el descuento."
            )

    def _crear_aviso_promocion(self, codigos_aplicados):
        candidatos = []
        for promocion in self.supermercado.listar_promociones():
            if promocion.codigo in codigos_aplicados:
                continue

            codigos_promocion = {
                condicion.codigo_producto
                for condicion in promocion.condiciones
            }
            if not any(
                self.cantidades.get(codigo, 0) > 0
                for codigo in codigos_promocion
            ):
                continue

            faltantes = []
            for condicion in promocion.condiciones:
                actual = self.cantidades.get(
                    condicion.codigo_producto, 0
                )
                faltan = max(0, condicion.cantidad - actual)
                if faltan:
                    producto = self.supermercado.obtener_producto(
                        condicion.codigo_producto
                    )
                    unidad = "unidad" if faltan == 1 else "unidades"
                    faltantes.append(f"{faltan} {unidad} de {producto.nombre}")

            if faltantes:
                candidatos.append(
                    (
                        sum(
                            max(
                                0,
                                condicion.cantidad
                                - self.cantidades.get(
                                    condicion.codigo_producto, 0
                                ),
                            )
                            for condicion in promocion.condiciones
                        ),
                        -promocion.descuento,
                        promocion.codigo,
                        promocion,
                        faltantes,
                    )
                )

        if not candidatos:
            promociones = self.supermercado.listar_promociones()
            if promociones and all(
                promocion.codigo in codigos_aplicados
                for promocion in promociones
            ):
                return "¡Ya alcanzo todas las promociones disponibles!"
            return ""

        _unidades, _descuento, _codigo, promocion, faltantes = min(
            candidatos
        )
        detalle = " y ".join(faltantes)
        return (
            f'Para alcanzar "{promocion.nombre}" '
            f"({promocion.descuento}%): agregue {detalle}."
        )

    def _confirmar_compra(self):
        if not self.cantidades:
            return

        texto = "\n".join(
            ["COMPRA"]
            + [
                f"PRODUCTO {codigo} CANTIDAD {cantidad}"
                for codigo, cantidad in self.cantidades.items()
            ]
            + ["FIN"]
        )
        errores = DSLCompras(self.supermercado).procesar(texto)
        if errores:
            messagebox.showerror(
                "No se pudo realizar la compra", "\n".join(errores)
            )
            return

        compra = self.supermercado.compras[-1]
        promociones = ", ".join(
            promocion.nombre for promocion in compra.promociones_aplicadas
        ) or "Ninguna"
        messagebox.showinfo(
            "Compra realizada",
            "Compra registrada correctamente.\n\n"
            f"Promociones aplicadas: {promociones}\n"
            f"Total final: $ {compra.importe_total:.2f}",
        )
        self.compra_realizada = True
        self._reiniciar_compra(
            "Compra registrada. Puede comenzar una nueva sin cerrar la ventana."
        )

    def mostrar(self):
        self.ventana.mainloop()
        return self.compra_realizada


def abrir_pantalla_compra(supermercado):
    """Abre la ventana de compra y devuelve si se registro una compra."""
    if not supermercado.listar_productos():
        return False
    try:
        return PantallaCompra(supermercado).mostrar()
    except tk.TclError as error:
        raise RuntimeError("la interfaz grafica no esta disponible") from error
