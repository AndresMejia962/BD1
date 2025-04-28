import mysql.connector
from tkinter import messagebox

# Conexión a la base de datos
def conectar_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="mi_contraseña123",
        database="inventario_facturacion"
    )

# Función para obtener los proveedores
def obtener_proveedores():
    try:
        db = conectar_db()
        cursor = db.cursor()
        cursor.execute("SELECT proveedor_id, nombre FROM proveedores")
        proveedores = cursor.fetchall()
        db.close()
        return proveedores
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo obtener los proveedores: {e}")
        return []

# Función para obtener los clientes
def obtener_clientes():
    try:
        db = conectar_db()
        cursor = db.cursor()
        cursor.execute("SELECT cliente_id, nombre FROM clientes")
        clientes = cursor.fetchall()
        db.close()
        return clientes
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo obtener los clientes: {e}")
        return []

# Función para obtener los empleados
def obtener_empleados():
    try:
        db = conectar_db()
        cursor = db.cursor()
        cursor.execute("SELECT empleado_id, nombre FROM empleados")
        empleados = cursor.fetchall()
        db.close()
        return empleados
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo obtener los empleados: {e}")
        return []

# Función para obtener los productos
def obtener_productos():
    try:
        db = conectar_db()
        cursor = db.cursor()
        cursor.execute("SELECT producto_id, nombre, precio, stock FROM productos")
        productos = cursor.fetchall()
        db.close()
        return productos
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo obtener los productos: {e}")
        return []