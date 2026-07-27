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

# Historial de cambios

## Versión 0.3.0

### Dashboard

• Corrección del contador de productos.
• Inventario bajo dinámico.

### Productos

• Edición de productos.
• Búsqueda por nombre y código.
• Actualización automática.
• Ventana mejorada.

### Inventario

• Stock mínimo configurable por producto.
• Dashboard usando stock mínimo personalizado.

### Estado

• Implementación de borrado lógico.
• Desactivar productos.
• Reactivar productos.
• Mostrar productos desactivados.
• Indicador Activo / Desactivado.

### Excel

• Exportar catálogo a Excel.
• Importar catálogo desde Excel.

### Mejoras generales

• Corrección de errores.
• Mejor organización del código.
• Optimización de consultas SQLite.
• Mejor comunicación entre ventanas.

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