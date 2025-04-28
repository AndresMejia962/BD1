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

## Estructura del Proyecto

El proyecto se organiza en varios archivos, cada uno con una funcionalidad específica:

- **`database.py`**: Contiene las funciones necesarias para interactuar con la base de datos MySQL, como la conexión y la obtención de datos (productos, proveedores, clientes, etc.).
- **`config.py`**: Archivo de configuración, donde se gestiona el rol de usuario.
- **`main.py`**: Punto de entrada de la aplicación, donde se configura la interfaz y se inicia la ventana de inicio de sesión.
- **`ui.py`**: Contiene las funciones para la interfaz gráfica, incluyendo la ventana de inicio de sesión y la ventana principal.
- **`business_logic.py`**: Contiene las funciones relacionadas con la lógica de negocio, como la gestión de productos, ventas y generación de reportes.
- **`reports.py`**: Contiene la lógica para generar reportes en formatos PDF y Excel.
- **`styles.py`**: Define los estilos de la interfaz gráfica.

## Uso

### Iniciar sesión

Al abrir la aplicación, aparecerá una ventana de inicio de sesión. Usa las credenciales predefinidas:

- **Usuario**: `andrea`, **Contraseña**: `admin123` (para administrador)
- **Usuario**: `pedro`, **Contraseña**: `empleado123` (para empleado)

### Interfaz principal

Después de iniciar sesión, accederás a la ventana principal donde podrás gestionar productos, proveedores, clientes y realizar ventas.

### Generación de reportes

Desde la interfaz principal, puedes generar reportes de ventas, inventario y pagos, y exportarlos a Excel o PDF.

### Seguridad

Los roles definen qué acciones puede realizar cada usuario. Los administradores pueden gestionar todo, mientras que los empleados solo pueden registrar ventas y consultar datos.

## Contribución

Si deseas contribuir al proyecto, por favor sigue estos pasos:

1. Realiza un fork del repositorio.
2. Crea una rama para tu nueva característica:  
   ```bash
   git checkout -b feature-nueva-caracteristica
