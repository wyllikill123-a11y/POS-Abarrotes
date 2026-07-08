# 📜 CHANGELOG

Todos los cambios importantes de RositaPOS quedarán registrados aquí.

---

# Versión 0.1.0 - Semilla

Fecha: 05/07/2026

## Agregado

- Creación del proyecto RositaPOS.
- Estructura principal de carpetas.
- Entorno virtual de Python.
- Configuración de VS Code.
- Integración de CustomTkinter.
- Creación de la ventana principal.
- Dashboard inicial.
- Menú lateral.
- Barra superior con fecha y hora.
- Base de datos SQLite.
- Rediseño de la base de datos con tablas:
  - Categorías
  - Marcas
  - Proveedores
  - Productos
- Creación de ROADMAP.md.
- Creación de CHANGELOG.md.
- Inicio del módulo Productos.
- Archivo `productos_window.py` creado.

---

## Estado del proyecto

🟢 Proyecto estable.

Próxima misión:

➡ Construir el módulo de Productos.

# Versión 0.3.0

## Agregado
- Registro de productos conectado a SQLite.
- Modelo Producto.
- Formulario para alta de productos.
- Campo Unidad mediante lista desplegable.
- Validación básica y mensajes de éxito/error.

# Versión 0.5.0 - 07/07/2026

## Productos

- Se agregó edición de productos.
- La misma ventana sirve para registrar y editar.
- El código del producto queda bloqueado durante la edición.
- La lista se actualiza automáticamente al cerrar la ventana.
- Se agregaron los métodos:
  - buscar_por_codigo()
  - actualizar()
- Se mejoró la estructura del modelo Producto.