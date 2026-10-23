# Entregable 3 - DSL de supermercado

Sistema en Python para administrar productos y promociones y registrar compras mediante un DSL interno y dos DSL externos implementados con Lark.

## Instalacion

```powershell
pip install -r requirements.txt
```

## Ejecucion

```powershell
python main.py
```

El menu permite procesar archivos de mantenimiento y compras, y consultar productos, promociones y compras registradas. La opcion 6 abre una pantalla que informa las promociones disponibles, avisa que productos faltan para alcanzar la promocion mas cercana y permite seleccionar productos, armar un carrito y confirmar varias compras sin cerrar la ventana. El resumen muestra en vivo el subtotal, los descuentos, las promociones aplicadas y el total. Hay entradas listas para probar en `ejemplos/mantenimiento.txt` y `ejemplos/compras.txt`.

## Pruebas

```powershell
python -m unittest discover -s tests -v
```
