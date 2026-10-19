# Requerimientos del Entregable 3 - DSL

Fuente: `Prog. Avanzada 2026 - Entregable 3 - DSL.pdf` (7 paginas).

Este archivo estructura la letra del proyecto para facilitar su implementacion y verificacion. No agrega requisitos que no esten en la consigna.

## 1. Objetivo y alcance

Implementar en Python un sistema de supermercado que permita:

- cargar productos y promociones;
- realizar compras;
- efectuar una carga inicial mediante un DSL interno;
- mantener productos y promociones mediante un primer DSL externo;
- registrar compras mediante un segundo DSL externo;
- consultar productos, promociones y compras desde un menu.

## 2. Modelo de dominio

### Producto

- Codigo.
- Nombre.
- Precio.
- Categoria opcional.

### Promocion

- Codigo.
- Nombre.
- Lista de condiciones, cada una con:
  - codigo de producto;
  - operador (`=` o `>=`);
  - cantidad.
- Porcentaje de descuento.

### Compra

- Lista de lineas, cada una con:
  - codigo de producto;
  - precio;
  - cantidad;
  - porcentaje de descuento;
  - importe (`precio * cantidad - importe del descuento`).
- Lista de promociones aplicadas, identificadas por codigo.
- Importe total, calculado como la suma de los importes de las lineas.

## 3. Reglas de promociones y descuentos

- Todas las condiciones de una promocion deben cumplirse para poder aplicarla.
- Una compra puede tener varias promociones aplicables.
- Para cada producto se debe elegir la promocion que produzca el mayor porcentaje de descuento.
- Las unidades de un mismo producto pueden repartirse entre promociones distintas; una promocion puede afectar algunas unidades y otra promocion las restantes.
- El descuento se aplica solamente a las unidades de los productos asociados con la promocion, no a toda la compra.
- Una promocion puede aplicarse multiples veces cuando las cantidades compradas permiten repetir todas sus condiciones.
- Las unidades sobrantes que no completan una promocion quedan sin descuento.

## 4. DSL interno y carga inicial

- La carga inicial de productos y promociones debe usar un DSL interno.
- Debe implementarse con Fluent Interface, encadenamiento de metodos y Expression Builders.
- El diseño debe permitir reemplazar con facilidad un DSL interno por otro.
- Debe existir una unica configuracion inicial del supermercado en el codigo fuente.
- La aplicacion debe ejecutar esa configuracion antes de mostrar el menu principal.
- Metodos de primer nivel:
  - `producto(codigo)`;
  - `promocion(codigo)`;
  - `finalizar()`.
- Metodos disponibles al definir un producto, sin orden fijo:
  - `nombre(nombre)`;
  - `precio(precio)`;
  - `categoria(categoria)`.
- Metodos disponibles al definir una promocion, sin orden fijo:
  - `nombre(nombre)`;
  - `descuento(porcentaje)`;
  - `cuando_producto(codigo_producto)`.
- Metodos disponibles despues de `cuando_producto`:
  - `cantidad_igual(cantidad)`;
  - `cantidad_mayor_igual(cantidad)`.
- Si no se especifica un metodo de cantidad, la condicion usa `cantidad = 1`.
- `finalizar()` cierra la carga y deja listo el supermercado.

## 5. Menu principal

Despues de la carga inicial, el sistema debe ofrecer:

1. Mantenimiento de productos y promociones mediante archivo y DSL externo.
2. Realizacion de compras mediante archivo y un DSL externo distinto.
3. Listado de productos con codigo, nombre, precio y categoria.
4. Listado de promociones con codigo, nombre, porcentaje de descuento y condiciones. Cada condicion debe mostrar codigo y nombre del producto, operador y cantidad.
5. Listado de compras con:
   - productos: codigo, nombre, cantidad, precio unitario, porcentaje de descuento e importe;
   - promociones aplicadas: codigo y nombre;
   - importe total.

## 6. DSL externo de mantenimiento

- Debe leer su entrada desde un archivo.
- Debe implementarse con PLY o Lark.
- Operaciones de primer nivel:
  - `AGREGAR PRODUCTO codigo ... FIN`;
  - `ACTUALIZAR PRODUCTO codigo ... FIN`;
  - `ELIMINAR PRODUCTO codigo`;
  - `AGREGAR PROMOCION codigo ... FIN`;
  - `ACTUALIZAR PROMOCION codigo ... FIN`;
  - `ELIMINAR PROMOCION codigo`.
- Atributos admitidos para agregar o actualizar productos:
  - `NOMBRE texto`;
  - `PRECIO numero`;
  - `CATEGORIA texto`.
- Atributos admitidos para agregar o actualizar promociones:
  - `NOMBRE texto`;
  - `DESCUENTO numero`;
  - `CUANDO`, seguido de una lista de condiciones.
- Forma de una condicion, en ese orden:
  - `PRODUCTO codigo CANTIDAD = numero`;
  - `PRODUCTO codigo CANTIDAD >= numero`;
  - `PRODUCTO codigo`, equivalente a cantidad 1.
- `CUANDO` no tiene un `FIN` propio; termina al comenzar otro atributo o al cerrar la operacion.
- Al actualizar, los atributos omitidos conservan su valor anterior.
- Si una actualizacion de promocion incluye `CUANDO`, todas las condiciones anteriores se reemplazan.

## 7. DSL externo de compras

- Debe ser distinto del DSL de mantenimiento y leer su entrada desde un archivo.
- Debe implementarse con PLY o Lark.
- Una compra tiene la forma `COMPRA ... FIN`.
- Dentro de una compra se admite una lista de:
  - `PRODUCTO codigo CANTIDAD numero`;
  - `PRODUCTO codigo`, equivalente a cantidad 1.
- Deben poder procesarse varias compras en un mismo archivo.

## 8. Validaciones semanticas y de datos

- Nombres y categorias: texto.
- Precios: numeros enteros o numeros con hasta dos decimales.
- Codigos y cantidades: numeros enteros.
- Al agregar un producto o promocion, su codigo no debe existir.
- Al modificar o eliminar un producto o promocion, su codigo debe existir.
- Todo producto asociado a una promocion debe existir.
- No se puede eliminar un producto asociado a una promocion.
- Una promocion no puede contener mas de una condicion para el mismo codigo de producto.
- Todo producto incluido en una compra debe existir.
- Producto: codigo, nombre y precio obligatorios; categoria opcional.
- Promocion: codigo, nombre y descuento obligatorios; debe tener al menos una condicion.
- Compra: debe tener al menos un producto.

## 9. Manejo de errores

- El parser debe detectar los errores sintacticos.
- El modelo semantico debe detectar los errores semanticos.
- Un error semantico no debe abortar el procesamiento completo del archivo.
- Las operaciones validas deben realizarse aunque otras operaciones del mismo archivo fallen.
- Al terminar se debe informar la lista de errores encontrados.

## 10. Requerimientos tecnicos

- Implementar un modelo semantico.
- Implementar el DSL interno mediante Expression Builders y encadenamiento de metodos.
- Implementar cada DSL externo con PLY y/o Lark.
- Requisito extra para grupos de tres integrantes: usar una herramienta para el DSL de mantenimiento y la otra para el DSL de compras; no se puede usar la misma en ambos.

## 11. Documentacion y entrega

- Entregar el codigo fuente.
- Entregar un informe tecnico en PDF que incluya como minimo:
  - decisiones de diseno e implementacion;
  - explicacion y justificacion de las herramientas utilizadas;
  - reglas de produccion;
  - breve conclusion sobre el producto y el aprendizaje obtenido.
- Entregar un ZIP llamado `Entregable3Apellido1Apellido2.zip`, con los apellidos de los integrantes.
- Maximo de tres integrantes por grupo.
- Fecha limite indicada en la letra: 27/10/2026 a las 12:00 por Moodle.
- Presentacion en clase indicada en la letra: 26/10/2026 o 27/10/2026, con presencia de todos los integrantes.
