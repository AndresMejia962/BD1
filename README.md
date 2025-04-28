# Sistema de Gestión de Inventario y Facturación

Este proyecto es una aplicación de gestión de inventarios y facturación para tiendas pequeñas y medianas. El sistema permite gestionar productos, proveedores, clientes y empleados, además de registrar ventas, generar facturas y reportes financieros. La aplicación está construida usando Python con Tkinter para la interfaz gráfica de usuario (GUI) y MySQL para la base de datos.

## Descripción

La aplicación está diseñada para facilitar la administración de inventarios y el procesamiento de ventas en tiempo real. Además, permite la generación de reportes de ventas, inventario y pagos. Los usuarios pueden iniciar sesión con roles definidos (administrador, empleado, etc.), y se implementa un control de acceso a diferentes funcionalidades según el rol.

### Características principales:
- **Gestión de productos**: Añadir, eliminar y actualizar productos en el inventario.
- **Gestión de proveedores**: Registrar y consultar proveedores.
- **Gestión de clientes**: Registrar y consultar clientes.
- **Gestión de empleados**: Añadir y gestionar empleados.
- **Registro de ventas**: Realizar ventas, generar facturas y actualizar el inventario automáticamente.
- **Generación de reportes**: Generación de reportes de ventas, inventario y pagos en formato PDF y Excel.
- **Seguridad**: Acceso controlado mediante autenticación de usuario y roles.

## Requisitos

Para ejecutar este proyecto necesitas tener instalado:

- Python 3.x
- MySQL
- Tkinter (viene incluido con la instalación estándar de Python)
- Bibliotecas adicionales de Python:
  - `mysql-connector`
  - `bcrypt`
  - `pandas`
  - `reportlab`
  - `matplotlib`

Puedes instalar las bibliotecas necesarias con el siguiente comando:

```bash
pip install mysql-connector-python bcrypt pandas reportlab matplotlib
