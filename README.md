# Sistema de Gestión de Inventario y Facturación

## 📋 Descripción
Sistema completo para la gestión de inventario y facturación, diseñado para pequeñas y medianas empresas. Permite el control de productos, ventas, clientes, proveedores y generación de reportes.

## 🚀 Características Principales

### Gestión de Inventario
- ✅ Alta, baja y modificación de productos
- 📦 Control de stock en tiempo real
- 🏷️ Categorización de productos
- 📊 Alertas de stock bajo

### Facturación
- 💰 Generación de facturas
- 🛒 Proceso de venta simplificado
- 💳 Múltiples formas de pago
- 🧾 Historial de ventas

### Gestión de Usuarios
- 👥 Sistema de roles (Administrador/Empleado)
- 🔐 Control de acceso basado en roles
- 👤 Gestión de perfiles de usuario

### Reportes
- 📈 Reportes de ventas
- 📉 Informes de inventario
- 📊 Estadísticas de productos
- 💹 Análisis financiero básico

## 🛠️ Tecnologías Utilizadas
- Python 3.11+
- Tkinter (Interfaz gráfica)
- MySQL (Base de datos)
- Bibliotecas adicionales:
  - bcrypt (Seguridad)
  - Pillow (Manejo de imágenes)
  - reportlab (Generación de PDFs)

## 📦 Instalación y Ejecución

### Opción 1: Ejecutable (.exe) - Recomendado
1. Descargar el archivo `GestionInventario.exe` de la sección de [Releases](https://github.com/AndresMejia962/BD1/releases)
2. Configurar la base de datos:
   - Ejecutar el script SQL `inventario_facturacion.sql` en MySQL
   - Configurar las credenciales en `config.py`
3. Hacer doble clic en `GestionInventario.exe` para ejecutar la aplicación

### Opción 2: Desde el código fuente (Para desarrolladores)
1. Clonar el repositorio:
```bash
git clone https://github.com/AndresMejia962/BD1.git
```

2. Instalar dependencias:
```bash
pip install -r requirements.txt
```

3. Configurar la base de datos:
- Ejecutar el script SQL `inventario_facturacion.sql`
- Configurar las credenciales en `config.py`

4. Ejecutar la aplicación:
```bash
python main.py
```

### Generar el ejecutable
Si deseas generar el ejecutable por tu cuenta:
1. Instalar PyInstaller:
```bash
pip install pyinstaller
```

2. Generar el ejecutable:
```bash
pyinstaller --name=GestionInventario --onefile --windowed --add-data "inventario_facturacion.sql;." --add-data "actualizar_usuarios.sql;." main.py
```

3. El ejecutable se generará en la carpeta `dist`

## 👤 Credenciales por Defecto

### Administrador
- Usuario: andrea
- Contraseña: admin123

### Empleado
- Usuario: pedro
- Contraseña: empleado123

## 📚 Estructura del Proyecto

- `main.py`: Punto de entrada de la aplicación
- `ui.py`: Interfaz gráfica de usuario
- `business_logic.py`: Lógica de negocio
- `database.py`: Conexión y operaciones con la base de datos
- `db_manager.py`: Gestión de la base de datos
- `reports.py`: Generación de reportes
- `config.py`: Configuración general
- `styles.py`: Estilos de la interfaz
- `shortcuts.py`: Atajos y utilidades

## 🔒 Seguridad
- Contraseñas hasheadas con bcrypt
- Control de acceso basado en roles
- Validación de entrada de datos
- Protección contra SQL injection

## 📋 Requisitos del Sistema
- Windows 10/11
- Python 3.11 o superior
- MySQL 8.0 o superior
- 4GB RAM mínimo
- 500MB espacio en disco

## 🤝 Contribución
1. Fork del repositorio
2. Crear una rama para tu característica
3. Commit de tus cambios
4. Push a la rama
5. Crear un Pull Request

## 📞 Soporte
Para soporte y consultas:
- Email: andres.mejia1@utp.edu.co
- Issues: Crear un issue en el repositorio

## 📄 Licencia
Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.
