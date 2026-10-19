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

El menu permite procesar archivos de mantenimiento y compras, y consultar productos, promociones y compras registradas. Hay entradas listas para probar en `ejemplos/mantenimiento.txt` y `ejemplos/compras.txt`.

## Pruebas

```powershell
python -m unittest discover -s tests -v
```
