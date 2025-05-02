import tkinter as tk
import bcrypt
import sys
from ui import ventana_inicio_sesion
# from database import conectar_db  # Eliminada porque ya no existe

if __name__ == "__main__":
    # Crear la ventana raíz
    ventana_raiz = tk.Tk()
    ventana_raiz.withdraw()  # Ocultar la ventana raíz inicialmente

    # Hashear las contraseñas para los usuarios
    contrasena_admin = "admin123"
    contrasena_empleado = "empleado123"

    hashed_admin = bcrypt.hashpw(contrasena_admin.encode('utf-8'), bcrypt.gensalt())
    hashed_empleado = bcrypt.hashpw(contrasena_empleado.encode('utf-8'), bcrypt.gensalt())

    # Actualizar las contraseñas hasheadas en la base de datos
    try:
        from db_manager import DatabaseManager
        db_manager = DatabaseManager()
        with db_manager.get_connection() as db:
            cursor = db.cursor()
            cursor.execute("UPDATE usuarios SET password = %s WHERE username = 'andrea'", (hashed_admin,))
            cursor.execute("UPDATE usuarios SET password = %s WHERE username = 'pedro'", (hashed_empleado,))
            db.commit()
    except Exception as e:
        print(f"Error al actualizar contraseñas: {e}")

    # Iniciar la aplicación con la ventana de login
    ventana_inicio_sesion(ventana_raiz)

    # Iniciar el bucle principal
    ventana_raiz.mainloop()