from tkinter import messagebox
from db_manager import DatabaseManager

# Instancia global del gestor de base de datos
db_manager = DatabaseManager()

def obtener_proveedores():
    """
    Obtiene la lista de proveedores con caché.
    """
    try:
        with db_manager.get_connection() as connection:
            cursor = connection.cursor()
            cursor.execute("""
                SELECT proveedor_id, nombre 
                FROM proveedores 
                ORDER BY nombre
            """)
            return cursor.fetchall()
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo obtener los proveedores: {e}")
        return []

def obtener_clientes():
    """
    Obtiene la lista de clientes con caché.
    """
    try:
        with db_manager.get_connection() as connection:
            cursor = connection.cursor()
            cursor.execute("""
                SELECT cliente_id, nombre 
                FROM clientes 
                ORDER BY nombre
            """)
            return cursor.fetchall()
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo obtener los clientes: {e}")
        return []

def obtener_empleados():
    """
    Obtiene la lista de empleados con caché.
    """
    try:
        with db_manager.get_connection() as connection:
            cursor = connection.cursor()
            cursor.execute("""
                SELECT usuario_id, nombre 
                FROM usuarios 
                ORDER BY nombre
            """)
            return cursor.fetchall()
    except Exception as e:
        print(f"Error al obtener empleados: {e}")
        return []

def obtener_productos():
    """
    Obtiene la lista de productos utilizando el caché.
    """
    try:
        productos_dict = db_manager.get_productos(use_cache=True)
        return [(p['producto_id'], p['nombre'], p['precio'], p['stock']) for p in productos_dict]
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo obtener los productos: {e}")
        return []

def ejecutar_consulta(query, params=None, fetchall=True):
    """
    Ejecuta una consulta SQL de manera segura.
    """
    try:
        with db_manager.get_connection() as connection:
            cursor = connection.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            if fetchall:
                return cursor.fetchall()
            return cursor.fetchone()
    except Exception as e:
        messagebox.showerror("Error", f"Error en la consulta: {e}")
        return None

def ejecutar_transaccion(queries_and_params):
    """
    Ejecuta múltiples consultas en una transacción.
    """
    try:
        with db_manager.get_connection() as connection:
            cursor = connection.cursor()
            for query, params in queries_and_params:
                cursor.execute(query, params)
            connection.commit()
            return True
    except Exception as e:
        messagebox.showerror("Error", f"Error en la transacción: {e}")
        return False

def obtener_estadisticas_dashboard():
    """
    Obtiene las estadísticas para el dashboard de manera optimizada.
    """
    try:
        return db_manager.get_ventas_dashboard()
    except Exception as e:
        messagebox.showerror("Error", f"No se pudieron obtener las estadísticas: {e}")
        return None