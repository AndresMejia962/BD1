import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from database import conectar_db, obtener_proveedores, obtener_productos, obtener_clientes, obtener_empleados
import pandas as pd
import config
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
import sys

global usuario_rol

def cerrar_ventana(ventana):
    if isinstance(ventana, tk.Tk):  # Si es la ventana principal
        ventana.quit()  # Termina el bucle principal
        ventana.destroy()  # Destruye la ventana
        sys.exit()  # Cierra la aplicación
    else:  # Si es una ventana secundaria
        if hasattr(ventana, 'master') and ventana.master:
            ventana.master.deiconify()  # Mostrar la ventana padre
        ventana.destroy()  # Cerrar solo esta ventana

def cerrar_ventana_secundaria(ventana_secundaria, ventana_principal=None):
    if ventana_principal:
        ventana_principal.deiconify()  # Mostrar la ventana principal
    ventana_secundaria.destroy()  # Cerrar la ventana secundaria

# Función para consultar productos
def consultar_productos(ventana_principal=None):
    if ventana_principal:
        ventana_principal.withdraw()

    try:
        db = conectar_db()
        cursor = db.cursor()
        cursor.execute("""
            SELECT p.producto_id, p.nombre, p.categoria, p.precio, p.stock, pr.nombre, p.descripcion 
            FROM productos p
            LEFT JOIN proveedores pr ON p.proveedor_id = pr.proveedor_id
        """)
        productos = cursor.fetchall()
        db.close()

        ventana_productos = tk.Toplevel()
        ventana_productos.title("Lista de Productos")
        ventana_productos.geometry("900x500")
        ventana_productos.config(bg="#263238")

        # Configurar el protocolo de cierre
        ventana_productos.protocol("WM_DELETE_WINDOW", lambda: cerrar_ventana_secundaria(ventana_productos, ventana_principal))

        frame_filtro = ttk.Frame(ventana_productos)
        frame_filtro.pack(fill="x", padx=10, pady=5)

        ttk.Label(frame_filtro, text="Filtrar por Nombre o Categoría:").pack(side="left")
        entry_filtro = ttk.Entry(frame_filtro)
        entry_filtro.pack(side="left", fill="x", expand=True, padx=5)

        frame_tabla = ttk.Frame(ventana_productos)
        frame_tabla.pack(fill="both", expand=True, padx=10, pady=10)

        columnas = ("ID", "Nombre", "Categoría", "Precio", "Stock", "Proveedor", "Descripción")
        tabla = ttk.Treeview(frame_tabla, columns=columnas, show="headings", height=15)

        def ordenar_columna(col, reverse):
            datos = [(tabla.set(item, col), item) for item in tabla.get_children()]
            try:
                datos.sort(key=lambda x: float(x[0]), reverse=reverse)
            except ValueError:
                datos.sort(reverse=reverse)
            for index, (val, item) in enumerate(datos):
                tabla.move(item, "", index)
            tabla.heading(col, command=lambda: ordenar_columna(col, not reverse))

        for col in columnas:
            tabla.heading(col, text=col, command=lambda c=col: ordenar_columna(c, False))
            tabla.column(col, anchor="center", width=120)

        tabla.column("Nombre", width=150)
        tabla.column("Categoría", width=130)
        tabla.column("Proveedor", width=150)
        tabla.column("Descripción", width=200)

        def filtrar_productos(event=None):
            filtro = entry_filtro.get().lower()
            for item in tabla.get_children():
                tabla.delete(item)
            for producto in productos:
                if filtro in producto[1].lower() or (producto[2] and filtro in producto[2].lower()):
                    tabla.insert("", tk.END, values=producto)

        entry_filtro.bind("<KeyRelease>", filtrar_productos)

        for producto in productos:
            tabla.insert("", tk.END, values=producto)

        tabla.bind("<Double-1>", lambda event: actualizar_producto())

        scrollbar = ttk.Scrollbar(frame_tabla, orient="vertical", command=tabla.yview)
        tabla.configure(yscrollcommand=scrollbar.set)

        tabla.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        frame_acciones = ttk.Frame(ventana_productos)
        frame_acciones.pack(fill="x", padx=10, pady=5)

        def actualizar_producto():
            seleccionado = tabla.selection()
            if not seleccionado:
                messagebox.showwarning("Advertencia", "Por favor, selecciona un producto para actualizar.")
                return

            item = tabla.item(seleccionado[0])
            producto_id = item['values'][0]
            nombre_actual = item['values'][1]
            categoria_actual = item['values'][2]
            precio_actual = item['values'][3]
            stock_actual = item['values'][4]
            proveedor_actual = item['values'][5]
            descripcion_actual = item['values'][6]

            proveedores = obtener_proveedores()
            proveedor_dict = {nombre: prov_id for prov_id, nombre in proveedores}
            proveedor_nombres = list(proveedor_dict.keys())

            ventana_actualizar = tk.Toplevel()
            ventana_actualizar.title("Actualizar Producto")
            ventana_actualizar.geometry("300x350")
            ventana_actualizar.configure(bg="#263238")  # Corregido el color de fondo

            frame = ttk.Frame(ventana_actualizar)  # Establecer fondo del frame
            frame.pack(padx=10, pady=10, fill="both", expand=True)

            ttk.Label(frame, text="Nombre:").pack()
            entry_nombre = ttk.Entry(frame)
            entry_nombre.insert(0, nombre_actual)
            entry_nombre.pack(fill="x", pady=5)

            ttk.Label(frame, text="Categoría:").pack()
            entry_categoria = ttk.Entry(frame)
            entry_categoria.insert(0, categoria_actual if categoria_actual else "")
            entry_categoria.pack(fill="x", pady=5)

            ttk.Label(frame, text="Precio:").pack()
            entry_precio = ttk.Entry(frame)
            entry_precio.insert(0, precio_actual)
            entry_precio.pack(fill="x", pady=5)

            ttk.Label(frame, text="Stock:").pack()
            entry_stock = ttk.Entry(frame)
            entry_stock.insert(0, stock_actual)
            entry_stock.pack(fill="x", pady=5)

            ttk.Label(frame, text="Proveedor:").pack()
            combo_proveedor = ttk.Combobox(frame, values=proveedor_nombres, state="readonly")
            combo_proveedor.set(proveedor_actual if proveedor_actual else "")
            combo_proveedor.pack(fill="x", pady=5)

            ttk.Label(frame, text="Descripción:").pack()
            entry_descripcion = ttk.Entry(frame)
            entry_descripcion.insert(0, descripcion_actual if descripcion_actual else "")
            entry_descripcion.pack(fill="x", pady=5)

            def guardar_cambios():
                try:
                    nuevo_nombre = entry_nombre.get().strip()
                    nueva_categoria = entry_categoria.get().strip()
                    nuevo_precio = entry_precio.get().strip()
                    nuevo_stock = entry_stock.get().strip()
                    nuevo_proveedor = combo_proveedor.get()
                    nueva_descripcion = entry_descripcion.get().strip()
                    proveedor_id = proveedor_dict.get(nuevo_proveedor) if nuevo_proveedor else None

                    if not nuevo_nombre:
                        messagebox.showerror("Error", "El nombre del producto es obligatorio.")
                        return
                    try:
                        nuevo_precio = float(nuevo_precio)
                        if nuevo_precio <= 0:
                            raise ValueError("El precio debe ser mayor que 0.")
                    except ValueError:
                        messagebox.showerror("Error", "El precio debe ser un número válido mayor que 0.")
                        return
                    try:
                        nuevo_stock = int(nuevo_stock)
                        if nuevo_stock < 0:
                            raise ValueError("El stock no puede ser negativo.")
                    except ValueError:
                        messagebox.showerror("Error", "El stock debe ser un número entero no negativo.")
                        return

                    db = conectar_db()
                    cursor = db.cursor()
                    cursor.execute("""
                        UPDATE productos 
                        SET nombre = %s, categoria = %s, precio = %s, stock = %s, proveedor_id = %s, descripcion = %s 
                        WHERE producto_id = %s
                    """, (nuevo_nombre, nueva_categoria, nuevo_precio, nuevo_stock, proveedor_id, nueva_descripcion, producto_id))
                    db.commit()
                    db.close()

                    messagebox.showinfo("Éxito", "Producto actualizado correctamente")
                    ventana_actualizar.destroy()
                    ventana_productos.destroy()
                    if ventana_principal:
                        ventana_principal.deiconify()
                    consultar_productos(ventana_principal)
                except Exception as e:
                    messagebox.showerror("Error", f"No se pudo actualizar: {e}")

            btn_guardar = ttk.Button(frame, text="Guardar Cambios", command=guardar_cambios, style="Custom.TButton")
            btn_guardar.pack(pady=10)

            btn_cancelar = ttk.Button(frame, text="Cancelar", command=lambda: cerrar_ventana_secundaria(ventana_actualizar, ventana_principal), style="Custom.TButton")
            btn_cancelar.pack(pady=5)

        def eliminar_producto():
            seleccionado = tabla.selection()
            if not seleccionado:
                messagebox.showwarning("Advertencia", "Por favor, selecciona un producto para eliminar.")
                return

            if not messagebox.askyesno("Confirmar", "¿Estás seguro de que deseas eliminar este producto?"):
                return

            item = tabla.item(seleccionado[0])
            producto_id = item['values'][0]

            try:
                db = conectar_db()
                cursor = db.cursor()
                cursor.execute("DELETE FROM productos WHERE producto_id = %s", (producto_id,))
                db.commit()
                db.close()

                messagebox.showinfo("Éxito", "Producto eliminado correctamente")
                ventana_productos.destroy()
                if ventana_principal:
                    ventana_principal.deiconify()
                consultar_productos(ventana_principal)
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo eliminar: {e}")

        btn_actualizar = ttk.Button(frame_acciones, text="Actualizar Producto", command=actualizar_producto, style="Custom.TButton")
        btn_actualizar.pack(side="left", padx=5)

        btn_eliminar = ttk.Button(frame_acciones, text="Eliminar Producto", command=eliminar_producto, style="Custom.TButton")
        btn_eliminar.pack(side="left", padx=5)

        btn_cerrar = ttk.Button(ventana_productos, text="Cerrar", command=lambda: cerrar_ventana_secundaria(ventana_productos, ventana_principal), style="Custom.TButton")
        btn_cerrar.pack(pady=10)

    except Exception as e:
        messagebox.showerror("Error", f"No se pudo consultar: {e}")

# Función para agregar un producto
def agregar_producto(ventana_principal=None):
    if ventana_principal:
        ventana_principal.withdraw()

    ventana_agregar = tk.Toplevel()
    ventana_agregar.title("Agregar Producto")
    ventana_agregar.geometry("300x400")
    ventana_agregar.configure(bg="#263238")

    # Configurar el protocolo de cierre
    ventana_agregar.protocol("WM_DELETE_WINDOW", lambda: cerrar_ventana_secundaria(ventana_agregar, ventana_principal))

    def guardar():
        nombre = entry_nombre.get().strip()
        categoria = entry_categoria.get().strip()
        precio = entry_precio.get().strip()
        stock = entry_stock.get().strip()
        proveedor = combo_proveedor.get()
        descripcion = entry_descripcion.get().strip()
        proveedor_id = proveedor_dict.get(proveedor) if proveedor else None

        if not nombre:
            messagebox.showerror("Error", "El nombre del producto es obligatorio.")
            return
        try:
            precio = float(precio)
            if precio <= 0:
                raise ValueError("El precio debe ser mayor que 0.")
        except ValueError:
            messagebox.showerror("Error", "El precio debe ser un número válido mayor que 0.")
            return
        try:
            stock = int(stock)
            if stock < 0:
                raise ValueError("El stock no puede ser negativo.")
        except ValueError:
            messagebox.showerror("Error", "El stock debe ser un número entero no negativo.")
            return

        try:
            db = conectar_db()
            cursor = db.cursor()
            cursor.execute("""
                INSERT INTO productos (nombre, categoria, precio, stock, proveedor_id, descripcion) 
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (nombre, categoria, precio, stock, proveedor_id, descripcion))
            db.commit()
            messagebox.showinfo("Éxito", "Producto agregado correctamente")
            db.close()
            ventana_agregar.destroy()
            if ventana_principal:
                ventana_principal.deiconify()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo agregar el producto: {e}")

    frame = ttk.Frame(ventana_agregar)
    frame.pack(padx=10, pady=10, fill="both", expand=True)

    ttk.Label(frame, text="Nombre:").pack()
    entry_nombre = ttk.Entry(frame)
    entry_nombre.pack(fill="x", pady=5)

    ttk.Label(frame, text="Categoría:").pack()
    entry_categoria = ttk.Entry(frame)
    entry_categoria.pack(fill="x", pady=5)

    ttk.Label(frame, text="Precio:").pack()
    entry_precio = ttk.Entry(frame)
    entry_precio.pack(fill="x", pady=5)

    ttk.Label(frame, text="Stock:").pack()
    entry_stock = ttk.Entry(frame)
    entry_stock.pack(fill="x", pady=5)

    proveedores = obtener_proveedores()
    proveedor_dict = {nombre: prov_id for prov_id, nombre in proveedores}
    proveedor_nombres = list(proveedor_dict.keys())

    ttk.Label(frame, text="Proveedor:").pack()
    combo_proveedor = ttk.Combobox(frame, values=proveedor_nombres, state="readonly")
    combo_proveedor.pack(fill="x", pady=5)

    ttk.Label(frame, text="Descripción:").pack()
    entry_descripcion = ttk.Entry(frame)
    entry_descripcion.pack(fill="x", pady=5)

    btn_guardar = ttk.Button(frame, text="Guardar", command=guardar, style="Custom.TButton")
    btn_guardar.pack(pady=10)

    btn_cancelar = ttk.Button(frame, text="Cancelar", command=ventana_agregar.destroy, style="Custom.TButton")
    btn_cancelar.pack(pady=5)


# Función para gestionar proveedores
def gestionar_proveedores(ventana_principal=None):
    if ventana_principal:
        ventana_principal.withdraw()

    if config.usuario_rol != "admin":
        messagebox.showwarning("Acceso Denegado", "Solo los administradores pueden gestionar proveedores.")
        if ventana_principal:
            ventana_principal.deiconify()
        return

    try:
        db = conectar_db()
        cursor = db.cursor()
        cursor.execute("SELECT proveedor_id, nombre, contacto, telefono, email, direccion FROM proveedores")
        proveedores = cursor.fetchall()
        db.close()

        ventana_proveedores = tk.Toplevel()
        ventana_proveedores.title("Gestión de Proveedores")
        ventana_proveedores.geometry("900x500")
        ventana_proveedores.config(bg="#263238")

        # Configurar el protocolo de cierre
        ventana_proveedores.protocol("WM_DELETE_WINDOW", lambda: cerrar_ventana_secundaria(ventana_proveedores, ventana_principal))

        frame_filtro = ttk.Frame(ventana_proveedores)
        frame_filtro.pack(fill="x", padx=10, pady=5)

        ttk.Label(frame_filtro, text="Filtrar por Nombre o Contacto:").pack(side="left")
        entry_filtro = ttk.Entry(frame_filtro)
        entry_filtro.pack(side="left", fill="x", expand=True, padx=5)

        frame_tabla = ttk.Frame(ventana_proveedores)
        frame_tabla.pack(fill="both", expand=True, padx=10, pady=10)

        columnas = ("ID", "Nombre", "Contacto", "Teléfono", "Email", "Dirección")
        tabla = ttk.Treeview(frame_tabla, columns=columnas, show="headings", height=15)

        def ordenar_columna(col, reverse):
            datos = [(tabla.set(item, col), item) for item in tabla.get_children()]
            try:
                datos.sort(key=lambda x: float(x[0]), reverse=reverse)
            except ValueError:
                datos.sort(reverse=reverse)
            for index, (val, item) in enumerate(datos):
                tabla.move(item, "", index)
            tabla.heading(col, command=lambda: ordenar_columna(col, not reverse))

        for col in columnas:
            tabla.heading(col, text=col, command=lambda c=col: ordenar_columna(c, False))
            tabla.column(col, anchor="center", width=120)

        tabla.column("Nombre", width=150)
        tabla.column("Contacto", width=150)
        tabla.column("Email", width=150)
        tabla.column("Dirección", width=200)

        def filtrar_proveedores(event=None):
            filtro = entry_filtro.get().lower()
            for item in tabla.get_children():
                tabla.delete(item)
            for proveedor in proveedores:
                if filtro in proveedor[1].lower() or (proveedor[2] and filtro in proveedor[2].lower()):
                    tabla.insert("", tk.END, values=proveedor)

        entry_filtro.bind("<KeyRelease>", filtrar_proveedores)

        for proveedor in proveedores:
            tabla.insert("", tk.END, values=proveedor)

        tabla.bind("<Double-1>", lambda event: actualizar_proveedor())

        scrollbar = ttk.Scrollbar(frame_tabla, orient="vertical", command=tabla.yview)
        tabla.configure(yscrollcommand=scrollbar.set)

        tabla.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        frame_acciones = ttk.Frame(ventana_proveedores)
        frame_acciones.pack(fill="x", padx=10, pady=5)

        def agregar_proveedor():
            def guardar():
                nombre = entry_nombre.get().strip()
                contacto = entry_contacto.get().strip()
                telefono = entry_telefono.get().strip()
                email = entry_email.get().strip()
                direccion = entry_direccion.get().strip()

                if not nombre:
                    messagebox.showerror("Error", "El nombre del proveedor es obligatorio.")
                    return
                if email and not "@" in email:
                    messagebox.showerror("Error", "El email debe tener un formato válido.")
                    return
                if telefono and not telefono.replace("+", "").isdigit():
                    messagebox.showerror("Error", "El teléfono debe contener solo números y opcionalmente un '+' al inicio.")
                    return

                try:
                    db = conectar_db()
                    cursor = db.cursor()
                    cursor.execute("""
                        INSERT INTO proveedores (nombre, contacto, telefono, email, direccion) 
                        VALUES (%s, %s, %s, %s, %s)
                    """, (nombre, contacto, telefono, email, direccion))
                    db.commit()
                    db.close()

                    messagebox.showinfo("Éxito", "Proveedor agregado correctamente")
                    ventana_agregar.destroy()
                    ventana_proveedores.destroy()
                    if ventana_principal:
                        ventana_principal.deiconify()
                    gestionar_proveedores(ventana_principal)
                except Exception as e:
                    messagebox.showerror("Error", f"No se pudo agregar el proveedor: {e}")

            ventana_agregar = tk.Toplevel()
            ventana_agregar.title("Agregar Proveedor")
            ventana_agregar.geometry("300x350")
            ventana_agregar.configure(bg="#263238")  # Updated background color

            frame = ttk.Frame(ventana_agregar)
            frame.pack(padx=10, pady=10, fill="both", expand=True)

            ttk.Label(frame, text="Nombre:").pack()
            entry_nombre = ttk.Entry(frame)
            entry_nombre.pack(fill="x", pady=5)

            ttk.Label(frame, text="Contacto:").pack()
            entry_contacto = ttk.Entry(frame)
            entry_contacto.pack(fill="x", pady=5)

            ttk.Label(frame, text="Teléfono:").pack()
            entry_telefono = ttk.Entry(frame)
            entry_telefono.pack(fill="x", pady=5)

            ttk.Label(frame, text="Email:").pack()
            entry_email = ttk.Entry(frame)
            entry_email.pack(fill="x", pady=5)

            ttk.Label(frame, text="Dirección:").pack()
            entry_direccion = ttk.Entry(frame)
            entry_direccion.pack(fill="x", pady=5)

            btn_guardar = ttk.Button(frame, text="Guardar", command=guardar, style="Custom.TButton")
            btn_guardar.pack(pady=10)

            btn_cancelar = ttk.Button(frame, text="Cancelar", command=ventana_agregar.destroy, style="Custom.TButton")
            btn_cancelar.pack(pady=5)

        def actualizar_proveedor():
            seleccionado = tabla.selection()
            if not seleccionado:
                messagebox.showwarning("Advertencia", "Por favor, selecciona un proveedor para actualizar.")
                return

            item = tabla.item(seleccionado[0])
            proveedor_id = item['values'][0]
            nombre_actual = item['values'][1]
            contacto_actual = item['values'][2]
            telefono_actual = item['values'][3]
            email_actual = item['values'][4]
            direccion_actual = item['values'][5]

            ventana_actualizar = tk.Toplevel()
            ventana_actualizar.title("Actualizar Proveedor")
            ventana_actualizar.geometry("300x350")
            ventana_actualizar.configure(bg="#263238")

            frame = ttk.Frame(ventana_actualizar)
            frame.pack(padx=10, pady=10, fill="both", expand=True)

            ttk.Label(frame, text="Nombre:").pack()
            entry_nombre = ttk.Entry(frame)
            entry_nombre.insert(0, nombre_actual)
            entry_nombre.pack(fill="x", pady=5)

            ttk.Label(frame, text="Contacto:").pack()
            entry_contacto = ttk.Entry(frame)
            entry_contacto.insert(0, contacto_actual if contacto_actual else "")
            entry_contacto.pack(fill="x", pady=5)

            ttk.Label(frame, text="Teléfono:").pack()
            entry_telefono = ttk.Entry(frame)
            entry_telefono.insert(0, telefono_actual if telefono_actual else "")
            entry_telefono.pack(fill="x", pady=5)

            ttk.Label(frame, text="Email:").pack()
            entry_email = ttk.Entry(frame)
            entry_email.insert(0, email_actual if email_actual else "")
            entry_email.pack(fill="x", pady=5)

            ttk.Label(frame, text="Dirección:").pack()
            entry_direccion = ttk.Entry(frame)
            entry_direccion.insert(0, direccion_actual if direccion_actual else "")
            entry_direccion.pack(fill="x", pady=5)

            def guardar_cambios():
                try:
                    nuevo_nombre = entry_nombre.get().strip()
                    nuevo_contacto = entry_contacto.get().strip()
                    nuevo_telefono = entry_telefono.get().strip()
                    nuevo_email = entry_email.get().strip()
                    nueva_direccion = entry_direccion.get().strip()

                    if not nuevo_nombre:
                        messagebox.showerror("Error", "El nombre del proveedor es obligatorio.")
                        return
                    if nuevo_email and not "@" in nuevo_email:
                        messagebox.showerror("Error", "El email debe tener un formato válido.")
                        return
                    if nuevo_telefono and not nuevo_telefono.replace("+", "").isdigit():
                        messagebox.showerror("Error", "El teléfono debe contener solo números y opcionalmente un '+' al inicio.")
                        return

                    db = conectar_db()
                    cursor = db.cursor()
                    cursor.execute("""
                        UPDATE proveedores 
                        SET nombre = %s, contacto = %s, telefono = %s, email = %s, direccion = %s 
                        WHERE proveedor_id = %s
                    """, (nuevo_nombre, nuevo_contacto, nuevo_telefono, nuevo_email, nueva_direccion, proveedor_id))
                    db.commit()
                    db.close()

                    messagebox.showinfo("Éxito", "Proveedor actualizado correctamente")
                    ventana_actualizar.destroy()
                    ventana_proveedores.destroy()
                    if ventana_principal:
                        ventana_principal.deiconify()
                    gestionar_proveedores(ventana_principal)
                except Exception as e:
                    messagebox.showerror("Error", f"No se pudo actualizar: {e}")

            btn_guardar = ttk.Button(frame, text="Guardar Cambios", command=guardar_cambios, style="Custom.TButton")
            btn_guardar.pack(pady=10)

            btn_cancelar = ttk.Button(frame, text="Cancelar", command=lambda: cerrar_ventana_secundaria(ventana_actualizar, ventana_principal), style="Custom.TButton")
            btn_cancelar.pack(pady=5)

        def eliminar_proveedor():
            seleccionado = tabla.selection()
            if not seleccionado:
                messagebox.showwarning("Advertencia", "Por favor, selecciona un proveedor para eliminar.")
                return

            if not messagebox.askyesno("Confirmar", "¿Estás seguro de que deseas eliminar este proveedor?"):
                return

            item = tabla.item(seleccionado[0])
            proveedor_id = item['values'][0]

            try:
                db = conectar_db()
                cursor = db.cursor()
                cursor.execute("DELETE FROM proveedores WHERE proveedor_id = %s", (proveedor_id,))
                db.commit()
                db.close()

                messagebox.showinfo("Éxito", "Proveedor eliminado correctamente")
                ventana_proveedores.destroy()
                if ventana_principal:
                    ventana_principal.deiconify()
                gestionar_proveedores(ventana_principal)
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo eliminar: {e}. Es posible que este proveedor esté asociado a productos.")

        btn_agregar = ttk.Button(frame_acciones, text="Agregar Proveedor", command=agregar_proveedor, style="Custom.TButton")
        btn_agregar.pack(side="left", padx=5)

        btn_actualizar = ttk.Button(frame_acciones, text="Actualizar Proveedor", command=actualizar_proveedor, style="Custom.TButton")
        btn_actualizar.pack(side="left", padx=5)

        btn_eliminar = ttk.Button(frame_acciones, text="Eliminar Proveedor", command=eliminar_proveedor, style="Custom.TButton")
        btn_eliminar.pack(side="left", padx=5)

        btn_cerrar = ttk.Button(ventana_proveedores, text="Cerrar", command=lambda: cerrar_ventana_secundaria(ventana_proveedores, ventana_principal), style="Custom.TButton")
        btn_cerrar.pack(pady=10)

    except Exception as e:
        messagebox.showerror("Error", f"No se pudo consultar los proveedores: {e}")

# Función para gestionar clientes
def gestionar_clientes(ventana_principal=None):
    if ventana_principal:
        ventana_principal.withdraw()

    if config.usuario_rol != "admin":
        messagebox.showwarning("Acceso Denegado", "Solo los administradores pueden gestionar clientes.")
        if ventana_principal:
            ventana_principal.deiconify()
        return

    try:
        db = conectar_db()
        cursor = db.cursor()
        cursor.execute("SELECT cliente_id, nombre, direccion, telefono, email, cedula FROM clientes")
        clientes = cursor.fetchall()
        db.close()

        ventana_clientes = tk.Toplevel()
        ventana_clientes.title("Gestión de Clientes")
        ventana_clientes.geometry("900x500")
        ventana_clientes.config(bg="#263238")

        # Configurar el protocolo de cierre
        ventana_clientes.protocol("WM_DELETE_WINDOW", lambda: cerrar_ventana_secundaria(ventana_clientes, ventana_principal))

        frame_filtro = ttk.Frame(ventana_clientes)
        frame_filtro.pack(fill="x", padx=10, pady=5)

        ttk.Label(frame_filtro, text="Filtrar por Nombre o Cédula:").pack(side="left")
        entry_filtro = ttk.Entry(frame_filtro)
        entry_filtro.pack(side="left", fill="x", expand=True, padx=5)

        frame_tabla = ttk.Frame(ventana_clientes)
        frame_tabla.pack(fill="both", expand=True, padx=10, pady=10)

        columnas = ("ID", "Nombre", "Dirección", "Teléfono", "Email", "Cédula")
        tabla = ttk.Treeview(frame_tabla, columns=columnas, show="headings", height=15)

        def ordenar_columna(col, reverse):
            datos = [(tabla.set(item, col), item) for item in tabla.get_children()]
            try:
                datos.sort(key=lambda x: float(x[0]), reverse=reverse)
            except ValueError:
                datos.sort(reverse=reverse)
            for index, (val, item) in enumerate(datos):
                tabla.move(item, "", index)
            tabla.heading(col, command=lambda: ordenar_columna(col, not reverse))

        for col in columnas:
            tabla.heading(col, text=col, command=lambda c=col: ordenar_columna(c, False))
            tabla.column(col, anchor="center", width=120)

        tabla.column("Nombre", width=150)
        tabla.column("Dirección", width=200)
        tabla.column("Email", width=150)
        tabla.column("Cédula", width=120)

        def filtrar_clientes(event=None):
            filtro = entry_filtro.get().lower()
            for item in tabla.get_children():
                tabla.delete(item)
            for cliente in clientes:
                if filtro in cliente[1].lower() or (cliente[5] and filtro in cliente[5].lower()):
                    tabla.insert("", tk.END, values=cliente)

        entry_filtro.bind("<KeyRelease>", filtrar_clientes)

        for cliente in clientes:
            tabla.insert("", tk.END, values=cliente)

        tabla.bind("<Double-1>", lambda event: actualizar_cliente())

        scrollbar = ttk.Scrollbar(frame_tabla, orient="vertical", command=tabla.yview)
        tabla.configure(yscrollcommand=scrollbar.set)

        tabla.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        frame_acciones = ttk.Frame(ventana_clientes)
        frame_acciones.pack(fill="x", padx=10, pady=5)

        def agregar_cliente():
            def guardar():
                nombre = entry_nombre.get().strip()
                direccion = entry_direccion.get().strip()
                telefono = entry_telefono.get().strip()
                email = entry_email.get().strip()
                cedula = entry_cedula.get().strip()

                if not nombre:
                    messagebox.showerror("Error", "El nombre del cliente es obligatorio.")
                    return
                if not cedula:
                    messagebox.showerror("Error", "La cédula del cliente es obligatoria.")
                    return
                if not cedula.isdigit() or len(cedula) < 8 or len(cedula) > 10:
                    messagebox.showerror("Error", "La cédula debe contener solo números y tener entre 8 y 10 dígitos.")
                    return
                if email and not "@" in email:
                    messagebox.showerror("Error", "El email debe tener un formato válido.")
                    return
                if telefono and not telefono.replace("+", "").isdigit():
                    messagebox.showerror("Error", "El teléfono debe contener solo números y opcionalmente un '+' al inicio.")
                    return

                try:
                    db = conectar_db()
                    cursor = db.cursor()
                    cursor.execute("""
                        INSERT INTO clientes (nombre, direccion, telefono, email, cedula) 
                        VALUES (%s, %s, %s, %s, %s)
                    """, (nombre, direccion, telefono, email, cedula))
                    db.commit()
                    db.close()

                    messagebox.showinfo("Éxito", "Cliente agregado correctamente")
                    ventana_agregar.destroy()
                    ventana_clientes.destroy()
                    if ventana_principal:
                        ventana_principal.deiconify()
                    gestionar_clientes(ventana_principal)
                except Exception as e:
                    messagebox.showerror("Error", f"No se pudo agregar el cliente: {e}")

            ventana_agregar = tk.Toplevel()
            ventana_agregar.title("Agregar Cliente")
            ventana_agregar.geometry("300x350")
            ventana_agregar.configure(bg="#263238")

            frame = ttk.Frame(ventana_agregar)
            frame.pack(padx=10, pady=10, fill="both", expand=True)

            ttk.Label(frame, text="Nombre:").pack()
            entry_nombre = ttk.Entry(frame)
            entry_nombre.pack(fill="x", pady=5)

            ttk.Label(frame, text="Dirección:").pack()
            entry_direccion = ttk.Entry(frame)
            entry_direccion.pack(fill="x", pady=5)

            ttk.Label(frame, text="Teléfono:").pack()
            entry_telefono = ttk.Entry(frame)
            entry_telefono.pack(fill="x", pady=5)

            ttk.Label(frame, text="Email:").pack()
            entry_email = ttk.Entry(frame)
            entry_email.pack(fill="x", pady=5)

            ttk.Label(frame, text="Cédula:").pack()
            entry_cedula = ttk.Entry(frame)
            entry_cedula.pack(fill="x", pady=5)

            btn_guardar = ttk.Button(frame, text="Guardar", command=guardar, style="Custom.TButton")
            btn_guardar.pack(pady=10)

            btn_cancelar = ttk.Button(frame, text="Cancelar", command=lambda: cerrar_ventana_secundaria(ventana_agregar, ventana_principal), style="Custom.TButton")
            btn_cancelar.pack(pady=5)

        def actualizar_cliente():
            seleccionado = tabla.selection()
            if not seleccionado:
                messagebox.showwarning("Advertencia", "Por favor, selecciona un cliente para actualizar.")
                return

            item = tabla.item(seleccionado[0])
            cliente_id = item['values'][0]
            nombre_actual = item['values'][1]
            direccion_actual = item['values'][2]
            telefono_actual = item['values'][3]
            email_actual = item['values'][4]
            cedula_actual = item['values'][5]

            ventana_actualizar = tk.Toplevel()
            ventana_actualizar.title("Actualizar Cliente")
            ventana_actualizar.geometry("300x350")
            ventana_actualizar.configure(bg="#263238")

            frame = ttk.Frame(ventana_actualizar)
            frame.pack(padx=10, pady=10, fill="both", expand=True)

            ttk.Label(frame, text="Nombre:").pack()
            entry_nombre = ttk.Entry(frame)
            entry_nombre.insert(0, nombre_actual)
            entry_nombre.pack(fill="x", pady=5)

            ttk.Label(frame, text="Dirección:").pack()
            entry_direccion = ttk.Entry(frame)
            entry_direccion.insert(0, direccion_actual if direccion_actual else "")
            entry_direccion.pack(fill="x", pady=5)

            ttk.Label(frame, text="Teléfono:").pack()
            entry_telefono = ttk.Entry(frame)
            entry_telefono.insert(0, telefono_actual if telefono_actual else "")
            entry_telefono.pack(fill="x", pady=5)

            ttk.Label(frame, text="Email:").pack()
            entry_email = ttk.Entry(frame)
            entry_email.insert(0, email_actual if email_actual else "")
            entry_email.pack(fill="x", pady=5)

            ttk.Label(frame, text="Cédula:").pack()
            entry_cedula = ttk.Entry(frame)
            entry_cedula.insert(0, cedula_actual)
            entry_cedula.pack(fill="x", pady=5)

            def guardar_cambios():
                try:
                    nuevo_nombre = entry_nombre.get().strip()
                    nueva_direccion = entry_direccion.get().strip()
                    nuevo_telefono = entry_telefono.get().strip()
                    nuevo_email = entry_email.get().strip()
                    nueva_cedula = entry_cedula.get().strip()

                    if not nuevo_nombre:
                        messagebox.showerror("Error", "El nombre del cliente es obligatorio.")
                        return
                    if not nueva_cedula:
                        messagebox.showerror("Error", "La cédula del cliente es obligatoria.")
                        return
                    if not nueva_cedula.isdigit() or len(nueva_cedula) < 8 or len(nueva_cedula) > 10:
                        messagebox.showerror("Error", "La cédula debe contener solo números y tener entre 8 y 10 dígitos.")
                        return
                    if nuevo_email and not "@" in nuevo_email:
                        messagebox.showerror("Error", "El email debe tener un formato válido.")
                        return
                    if nuevo_telefono and not nuevo_telefono.replace("+", "").isdigit():
                        messagebox.showerror("Error", "El teléfono debe contener solo números y opcionalmente un '+' al inicio.")
                        return

                    db = conectar_db()
                    cursor = db.cursor()
                    cursor.execute("""
                        UPDATE clientes 
                        SET nombre = %s, direccion = %s, telefono = %s, email = %s, cedula = %s 
                        WHERE cliente_id = %s
                    """, (nuevo_nombre, nueva_direccion, nuevo_telefono, nuevo_email, nueva_cedula, cliente_id))
                    db.commit()
                    db.close()

                    messagebox.showinfo("Éxito", "Cliente actualizado correctamente")
                    ventana_actualizar.destroy()
                    ventana_clientes.destroy()
                    if ventana_principal:
                        ventana_principal.deiconify()
                    gestionar_clientes(ventana_principal)
                except Exception as e:
                    messagebox.showerror("Error", f"No se pudo actualizar: {e}")

            btn_guardar = ttk.Button(frame, text="Guardar Cambios", command=guardar_cambios, style="Custom.TButton")
            btn_guardar.pack(pady=10)

            btn_cancelar = ttk.Button(frame, text="Cancelar", command=lambda: cerrar_ventana_secundaria(ventana_actualizar, ventana_principal), style="Custom.TButton")
            btn_cancelar.pack(pady=5)

        def eliminar_cliente():
            seleccionado = tabla.selection()
            if not seleccionado:
                messagebox.showwarning("Advertencia", "Por favor, selecciona un cliente para eliminar.")
                return

            if not messagebox.askyesno("Confirmar", "¿Estás seguro de que deseas eliminar este cliente?"):
                return

            item = tabla.item(seleccionado[0])
            cliente_id = item['values'][0]

            try:
                db = conectar_db()
                cursor = db.cursor()
                cursor.execute("DELETE FROM clientes WHERE cliente_id = %s", (cliente_id,))
                db.commit()
                db.close()

                messagebox.showinfo("Éxito", "Cliente eliminado correctamente")
                ventana_clientes.destroy()
                if ventana_principal:
                    ventana_principal.deiconify()
                gestionar_clientes(ventana_principal)
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo eliminar: {e}. Es posible que este cliente esté asociado a pedidos.")

        btn_agregar = ttk.Button(frame_acciones, text="Agregar Cliente", command=agregar_cliente, style="Custom.TButton")
        btn_agregar.pack(side="left", padx=5)

        btn_actualizar = ttk.Button(frame_acciones, text="Actualizar Cliente", command=actualizar_cliente, style="Custom.TButton")
        btn_actualizar.pack(side="left", padx=5)

        btn_eliminar = ttk.Button(frame_acciones, text="Eliminar Cliente", command=eliminar_cliente, style="Custom.TButton")
        btn_eliminar.pack(side="left", padx=5)

        btn_cerrar = ttk.Button(ventana_clientes, text="Cerrar", command=lambda: cerrar_ventana_secundaria(ventana_clientes, ventana_principal), style="Custom.TButton")
        btn_cerrar.pack(pady=10)

    except Exception as e:
        messagebox.showerror("Error", f"No se pudo consultar los clientes: {e}")

# Función para gestionar empleados
def gestionar_empleados(ventana_principal=None):
    if ventana_principal:
        ventana_principal.withdraw()

    if config.usuario_rol != "admin":
        messagebox.showwarning("Acceso Denegado", "Solo los administradores pueden gestionar empleados.")
        if ventana_principal:
            ventana_principal.deiconify()
        return

    try:
        db = conectar_db()
        cursor = db.cursor()
        cursor.execute("SELECT empleado_id, nombre, cargo, telefono, email FROM empleados")
        empleados = cursor.fetchall()
        db.close()

        ventana_empleados = tk.Toplevel()
        ventana_empleados.title("Gestión de Empleados")
        ventana_empleados.geometry("900x500")
        ventana_empleados.config(bg="#263238")

        # Configurar el protocolo de cierre
        ventana_empleados.protocol("WM_DELETE_WINDOW", lambda: cerrar_ventana_secundaria(ventana_empleados, ventana_principal))

        frame_filtro = ttk.Frame(ventana_empleados)
        frame_filtro.pack(fill="x", padx=10, pady=5)

        ttk.Label(frame_filtro, text="Filtrar por Nombre o Cargo:").pack(side="left")
        entry_filtro = ttk.Entry(frame_filtro)
        entry_filtro.pack(side="left", fill="x", expand=True, padx=5)

        frame_tabla = ttk.Frame(ventana_empleados)
        frame_tabla.pack(fill="both", expand=True, padx=10, pady=10)

        columnas = ("ID", "Nombre", "Cargo", "Teléfono", "Email")
        tabla = ttk.Treeview(frame_tabla, columns=columnas, show="headings", height=15)

        def ordenar_columna(col, reverse):
            datos = [(tabla.set(item, col), item) for item in tabla.get_children()]
            try:
                datos.sort(key=lambda x: float(x[0]), reverse=reverse)
            except ValueError:
                datos.sort(reverse=reverse)
            for index, (val, item) in enumerate(datos):
                tabla.move(item, "", index)
            tabla.heading(col, command=lambda: ordenar_columna(col, not reverse))

        for col in columnas:
            tabla.heading(col, text=col, command=lambda c=col: ordenar_columna(c, False))
            tabla.column(col, anchor="center", width=120)

        tabla.column("Nombre", width=150)
        tabla.column("Cargo", width=150)
        tabla.column("Email", width=150)

        def filtrar_empleados(event=None):
            filtro = entry_filtro.get().lower()
            for item in tabla.get_children():
                tabla.delete(item)
            for empleado in empleados:
                if filtro in empleado[1].lower() or (empleado[2] and filtro in empleado[2].lower()):
                    tabla.insert("", tk.END, values=empleado)

        entry_filtro.bind("<KeyRelease>", filtrar_empleados)

        for empleado in empleados:
            tabla.insert("", tk.END, values=empleado)

        tabla.bind("<Double-1>", lambda event: actualizar_empleado())

        scrollbar = ttk.Scrollbar(frame_tabla, orient="vertical", command=tabla.yview)
        tabla.configure(yscrollcommand=scrollbar.set)

        tabla.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        frame_acciones = ttk.Frame(ventana_empleados)
        frame_acciones.pack(fill="x", padx=10, pady=5)

        def agregar_empleado():
            def guardar():
                nombre = entry_nombre.get().strip()
                cargo = entry_cargo.get().strip()
                telefono = entry_telefono.get().strip()
                email = entry_email.get().strip()

                if not nombre:
                    messagebox.showerror("Error", "El nombre del empleado es obligatorio.")
                    return
                if not cargo:
                    messagebox.showerror("Error", "El cargo del empleado es obligatorio.")
                    return
                if email and not "@" in email:
                    messagebox.showerror("Error", "El email debe tener un formato válido.")
                    return
                if telefono and not telefono.replace("+", "").isdigit():
                    messagebox.showerror("Error", "El teléfono debe contener solo números y opcionalmente un '+' al inicio.")
                    return

                try:
                    db = conectar_db()
                    cursor = db.cursor()
                    cursor.execute("""
                        INSERT INTO empleados (nombre, cargo, telefono, email) 
                        VALUES (%s, %s, %s, %s)
                    """, (nombre, cargo, telefono, email))
                    db.commit()
                    db.close()

                    messagebox.showinfo("Éxito", "Empleado agregado correctamente")
                    ventana_agregar.destroy()
                    ventana_empleados.destroy()
                    if ventana_principal:
                        ventana_principal.deiconify()
                    gestionar_empleados(ventana_principal)
                except Exception as e:
                    messagebox.showerror("Error", f"No se pudo agregar el empleado: {e}")

            ventana_agregar = tk.Toplevel()
            ventana_agregar.title("Agregar Empleado")
            ventana_agregar.geometry("300x300")
            ventana_agregar.configure(bg="#263238")

            frame = ttk.Frame(ventana_agregar)
            frame.pack(padx=10, pady=10, fill="both", expand=True)

            ttk.Label(frame, text="Nombre:").pack()
            entry_nombre = ttk.Entry(frame)
            entry_nombre.pack(fill="x", pady=5)

            ttk.Label(frame, text="Cargo:").pack()
            entry_cargo = ttk.Entry(frame)
            entry_cargo.pack(fill="x", pady=5)

            ttk.Label(frame, text="Teléfono:").pack()
            entry_telefono = ttk.Entry(frame)
            entry_telefono.pack(fill="x", pady=5)

            ttk.Label(frame, text="Email:").pack()
            entry_email = ttk.Entry(frame)
            entry_email.pack(fill="x", pady=5)

            btn_guardar = ttk.Button(frame, text="Guardar", command=guardar, style="Custom.TButton")
            btn_guardar.pack(pady=10)

            btn_cancelar = ttk.Button(frame, text="Cancelar", command=ventana_agregar.destroy, style="Custom.TButton")
            btn_cancelar.pack(pady=5)

        def actualizar_empleado():
            seleccionado = tabla.selection()
            if not seleccionado:
                messagebox.showwarning("Advertencia", "Por favor, selecciona un empleado para actualizar.")
                return

            item = tabla.item(seleccionado[0])
            empleado_id = item['values'][0]
            nombre_actual = item['values'][1]
            cargo_actual = item['values'][2]
            telefono_actual = item['values'][3]
            email_actual = item['values'][4]

            ventana_actualizar = tk.Toplevel()
            ventana_actualizar.title("Actualizar Empleado")
            ventana_actualizar.geometry("300x300")
            ventana_actualizar.configure(bg="#263238")

            frame = ttk.Frame(ventana_actualizar)
            frame.pack(padx=10, pady=10, fill="both", expand=True)

            ttk.Label(frame, text="Nombre:").pack()
            entry_nombre = ttk.Entry(frame)
            entry_nombre.insert(0, nombre_actual)
            entry_nombre.pack(fill="x", pady=5)

            ttk.Label(frame, text="Cargo:").pack()
            entry_cargo = ttk.Entry(frame)
            entry_cargo.insert(0, cargo_actual)
            entry_cargo.pack(fill="x", pady=5)

            ttk.Label(frame, text="Teléfono:").pack()
            entry_telefono = ttk.Entry(frame)
            entry_telefono.insert(0, telefono_actual if telefono_actual else "")
            entry_telefono.pack(fill="x", pady=5)

            ttk.Label(frame, text="Email:").pack()
            entry_email = ttk.Entry(frame)
            entry_email.insert(0, email_actual if email_actual else "")
            entry_email.pack(fill="x", pady=5)

            def guardar_cambios():
                try:
                    nuevo_nombre = entry_nombre.get().strip()
                    nuevo_cargo = entry_cargo.get().strip()
                    nuevo_telefono = entry_telefono.get().strip()
                    nuevo_email = entry_email.get().strip()

                    if not nuevo_nombre:
                        messagebox.showerror("Error", "El nombre del empleado es obligatorio.")
                        return
                    if not nuevo_cargo:
                        messagebox.showerror("Error", "El cargo del empleado es obligatorio.")
                        return
                    if nuevo_email and not "@" in nuevo_email:
                        messagebox.showerror("Error", "El email debe tener un formato válido.")
                        return
                    if nuevo_telefono and not nuevo_telefono.replace("+", "").isdigit():
                        messagebox.showerror("Error", "El teléfono debe contener solo números y opcionalmente un '+' al inicio.")
                        return

                    db = conectar_db()
                    cursor = db.cursor()
                    cursor.execute("""
                        UPDATE empleados 
                        SET nombre = %s, cargo = %s, telefono = %s, email = %s 
                        WHERE empleado_id = %s
                    """, (nuevo_nombre, nuevo_cargo, nuevo_telefono, nuevo_email, empleado_id))
                    db.commit()
                    db.close()

                    messagebox.showinfo("Éxito", "Empleado actualizado correctamente")
                    ventana_actualizar.destroy()
                    ventana_empleados.destroy()
                    if ventana_principal:
                        ventana_principal.deiconify()
                    gestionar_empleados(ventana_principal)
                except Exception as e:
                    messagebox.showerror("Error", f"No se pudo actualizar: {e}")

            btn_guardar = ttk.Button(frame, text="Guardar Cambios", command=guardar_cambios, style="Custom.TButton")
            btn_guardar.pack(pady=10)

            btn_cancelar = ttk.Button(frame, text="Cancelar", command=lambda: cerrar_ventana_secundaria(ventana_actualizar, ventana_principal), style="Custom.TButton")
            btn_cancelar.pack(pady=5)

        def eliminar_empleado():
            seleccionado = tabla.selection()
            if not seleccionado:
                messagebox.showwarning("Advertencia", "Por favor, selecciona un empleado para eliminar.")
                return

            if not messagebox.askyesno("Confirmar", "¿Estás seguro de que deseas eliminar este empleado?"):
                return

            item = tabla.item(seleccionado[0])
            empleado_id = item['values'][0]

            try:
                db = conectar_db()
                cursor = db.cursor()
                cursor.execute("DELETE FROM empleados WHERE empleado_id = %s", (empleado_id,))
                db.commit()
                db.close()

                messagebox.showinfo("Éxito", "Empleado eliminado correctamente")
                ventana_empleados.destroy()
                if ventana_principal:
                    ventana_principal.deiconify()
                gestionar_empleados(ventana_principal)
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo eliminar: {e}. Es posible que este empleado esté asociado a pedidos.")

        btn_agregar = ttk.Button(frame_acciones, text="Agregar Empleado", command=agregar_empleado, style="Custom.TButton")
        btn_agregar.pack(side="left", padx=5)

        btn_actualizar = ttk.Button(frame_acciones, text="Actualizar Empleado", command=actualizar_empleado, style="Custom.TButton")
        btn_actualizar.pack(side="left", padx=5)

        btn_eliminar = ttk.Button(frame_acciones, text="Eliminar Empleado", command=eliminar_empleado, style="Custom.TButton")
        btn_eliminar.pack(side="left", padx=5)

        btn_cerrar = ttk.Button(ventana_empleados, text="Cerrar", command=lambda: cerrar_ventana_secundaria(ventana_empleados, ventana_principal), style="Custom.TButton")
        btn_cerrar.pack(pady=10)

    except Exception as e:
        messagebox.showerror("Error", f"No se pudo consultar los empleados: {e}")

# Función para registrar una venta
def registrar_venta(ventana_principal=None):
    if ventana_principal:
        ventana_principal.withdraw()

    clientes = obtener_clientes()
    cliente_dict = {nombre: cliente_id for cliente_id, nombre in clientes}
    cliente_nombres = list(cliente_dict.keys())

    productos = obtener_productos()
    producto_dict = {nombre: (producto_id, precio, stock) for producto_id, nombre, precio, stock in productos}
    producto_nombres = list(producto_dict.keys())

    ventana_venta = tk.Toplevel()
    ventana_venta.title("Registrar Venta")
    ventana_venta.geometry("800x600")
    ventana_venta.config(bg="#263238")

    # Configurar el protocolo de cierre
    ventana_venta.protocol("WM_DELETE_WINDOW", lambda: cerrar_ventana_secundaria(ventana_venta, ventana_principal))

    frame_form = ttk.LabelFrame(ventana_venta, text="Datos de la Venta", padding=10, style="Custom.TFrame")
    frame_form.pack(fill="x", padx=10, pady=10)

    ttk.Label(frame_form, text="Cliente (Opcional):").grid(row=0, column=0, padx=5, pady=5, sticky="w")
    combo_cliente = ttk.Combobox(frame_form, values=cliente_nombres, state="readonly")
    combo_cliente.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

    ttk.Label(frame_form, text="Cliente No Registrado (Nombre):").grid(row=1, column=0, padx=5, pady=5, sticky="w")
    entry_nombre_no_registrado = ttk.Entry(frame_form)
    entry_nombre_no_registrado.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

    ttk.Label(frame_form, text="Cédula No Registrado:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
    entry_cedula_no_registrado = ttk.Entry(frame_form)
    entry_cedula_no_registrado.grid(row=2, column=1, padx=5, pady=5, sticky="ew")

    ttk.Label(frame_form, text="Método de Pago:").grid(row=3, column=0, padx=5, pady=5, sticky="w")
    combo_metodo_pago = ttk.Combobox(frame_form, values=["Efectivo", "Tarjeta", "Transferencia"], state="readonly")
    combo_metodo_pago.grid(row=3, column=1, padx=5, pady=5, sticky="ew")

    frame_form.columnconfigure(1, weight=1)

    frame_productos = ttk.LabelFrame(ventana_venta, text="Productos", padding=10, style="Custom.TFrame")
    frame_productos.pack(fill="both", expand=True, padx=10, pady=10)

    frame_seleccion = ttk.Frame(frame_productos)
    frame_seleccion.pack(fill="x", pady=5)

    ttk.Label(frame_seleccion, text="Producto:").pack(side="left", padx=5)
    combo_producto = ttk.Combobox(frame_seleccion, values=producto_nombres, state="readonly")
    combo_producto.pack(side="left", fill="x", expand=True, padx=5)

    ttk.Label(frame_seleccion, text="Cantidad:").pack(side="left", padx=5)
    entry_cantidad = ttk.Entry(frame_seleccion, width=10)
    entry_cantidad.pack(side="left", padx=5)

    columnas = ("ID", "Nombre", "Cantidad", "Precio Unitario", "Subtotal")
    tabla = ttk.Treeview(frame_productos, columns=columnas, show="headings", height=10)

    for col in columnas:
        tabla.heading(col, text=col)
        tabla.column(col, anchor="center", width=120)

    tabla.pack(fill="both", expand=True)

    def agregar_producto():
        producto = combo_producto.get()
        if not producto:
            messagebox.showwarning("Advertencia", "Por favor, selecciona un producto.")
            return

        try:
            cantidad = int(entry_cantidad.get())
            if cantidad <= 0:
                raise ValueError("La cantidad debe ser mayor que 0.")
        except ValueError:
            messagebox.showwarning("Advertencia", "Por favor, ingresa una cantidad válida.")
            return

        producto_id, precio, stock = producto_dict[producto]
        if cantidad > stock:
            messagebox.showerror("Error", f"No hay suficiente stock. Disponible: {stock} unidades.")
            return

        subtotal = precio * cantidad
        tabla.insert("", tk.END, values=(producto_id, producto, cantidad, precio, subtotal))
        actualizar_total()

    def eliminar_producto():
        seleccionado = tabla.selection()
        if not seleccionado:
            messagebox.showwarning("Advertencia", "Por favor, selecciona un producto para eliminar.")
            return
        tabla.delete(seleccionado[0])
        actualizar_total()

    def actualizar_total():
        total = 0
        for item in tabla.get_children():
            valores = tabla.item(item)['values']
            total += float(valores[4])
        label_total.config(text=f"Total: ${total:.2f}")
        return total

    btn_agregar = ttk.Button(frame_seleccion, text="Agregar Producto", command=agregar_producto, style="Custom.TButton")
    btn_agregar.pack(side="left", padx=5, pady=5)

    btn_eliminar = ttk.Button(frame_seleccion, text="Eliminar Producto", command=eliminar_producto, style="Custom.TButton")
    btn_eliminar.pack(side="left", padx=5, pady=5)

    label_total = ttk.Label(frame_productos, text="Total: $0.00")
    label_total.pack(pady=5)

    def guardar_venta():
        cliente = combo_cliente.get()
        metodo_pago = combo_metodo_pago.get()
        nombre_no_registrado = entry_nombre_no_registrado.get().strip()
        cedula_no_registrado = entry_cedula_no_registrado.get().strip()

        if not metodo_pago:
            messagebox.showwarning("Advertencia", "Por favor, selecciona un método de pago.")
            return

        if not tabla.get_children():
            messagebox.showwarning("Advertencia", "Debes agregar al menos un producto a la venta.")
            return

        cliente_id = cliente_dict.get(cliente) if cliente else None
        total = actualizar_total()
        fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if not cliente:
            if not nombre_no_registrado and not cedula_no_registrado:
                nombre_no_registrado = None
                cedula_no_registrado = None
            elif not nombre_no_registrado:
                messagebox.showwarning("Advertencia", "Por favor, ingresa el nombre del cliente no registrado.")
                return
            elif not cedula_no_registrado:
                messagebox.showwarning("Advertencia", "Por favor, ingresa la cédula del cliente no registrado.")
                return
            else:
                if cedula_no_registrado and (not cedula_no_registrado.isdigit() or len(cedula_no_registrado) < 8 or len(cedula_no_registrado) > 10):
                    messagebox.showwarning("Advertencia", "La cédula debe contener solo números y tener entre 8 y 10 dígitos.")
                    return

        try:
            db = conectar_db()
            cursor = db.cursor()

            cursor.execute("""
                SELECT p.pedido_id, p.fecha, c.nombre, u.nombre, p.total, p.nombre_cliente_no_registrado, p.cedula_cliente_no_registrado
                FROM pedidos p
                LEFT JOIN clientes c ON p.cliente_id = c.cliente_id
                LEFT JOIN usuarios u ON p.usuario_id = u.usuario_id
            """)
            ventas = cursor.fetchall()

            cursor.execute("""
                INSERT INTO pedidos (cliente_id, usuario_id, fecha, total, nombre_cliente_no_registrado, cedula_cliente_no_registrado) 
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (cliente_id, config.usuario_id, fecha, total, nombre_no_registrado, cedula_no_registrado))
            pedido_id = cursor.lastrowid

            for item in tabla.get_children():
                valores = tabla.item(item)['values']
                producto_id = valores[0]
                cantidad = valores[2]
                precio_unitario = valores[3]

                cursor.execute("""
                    INSERT INTO pedido_detalle (pedido_id, producto_id, cantidad, precio_unitario) 
                    VALUES (%s, %s, %s, %s)
                """, (pedido_id, producto_id, cantidad, precio_unitario))

                cursor.execute("UPDATE productos SET stock = stock - %s WHERE producto_id = %s", (cantidad, producto_id))

            numero_factura = f"FAC-{pedido_id:06d}"
            cursor.execute("""
                INSERT INTO facturas (pedido_id, numero_factura, fecha_emision, total) 
                VALUES (%s, %s, %s, %s)
            """, (pedido_id, numero_factura, fecha, total))

            cursor.execute("""
                INSERT INTO pagos (pedido_id, fecha_pago, monto, metodo_pago) 
                VALUES (%s, %s, %s, %s)
            """, (pedido_id, fecha, total, metodo_pago))

            db.commit()
            db.close()

            if cliente:
                cliente_mostrar = cliente
            else:
                cliente_mostrar = f"{nombre_no_registrado} (Cédula: {cedula_no_registrado})" if nombre_no_registrado else "Cliente no registrado"
            factura_texto = f"Factura: {numero_factura}\nFecha: {fecha}\nCliente: {cliente_mostrar}\nVendedor: {config.usuario_nombre}\nMétodo de Pago: {metodo_pago}\nTotal: ${total:.2f}\n\nDetalles:\n"
            for item in tabla.get_children():
                valores = tabla.item(item)['values']
                factura_texto += f"- {valores[1]}: {valores[2]} x ${valores[3]} = ${valores[4]}\n"
            messagebox.showinfo("Factura Generada", factura_texto)

            ventana_venta.destroy()
            if ventana_principal:
                ventana_principal.deiconify()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo registrar la venta: {e}")

    btn_guardar = ttk.Button(ventana_venta, text="Guardar Venta", command=guardar_venta, style="Custom.TButton")
    btn_guardar.pack(pady=10)

    btn_cancelar = ttk.Button(ventana_venta, text="Cancelar", command=lambda: cerrar_ventana_secundaria(ventana_venta, ventana_principal), style="Custom.TButton")
    btn_cancelar.pack(pady=5)

# Función para generar reportes
def generar_reportes(ventana_principal=None):
    if ventana_principal:
        ventana_principal.withdraw()

    ventana_reportes = tk.Toplevel()
    ventana_reportes.title("Generar Reportes")
    ventana_reportes.geometry("800x500")
    ventana_reportes.config(bg="#263238")

    # Configurar el protocolo de cierre
    ventana_reportes.protocol("WM_DELETE_WINDOW", lambda: cerrar_ventana_secundaria(ventana_reportes, ventana_principal))

    frame = ttk.Frame(ventana_reportes)
    frame.pack(padx=10, pady=10, fill="both", expand=True)

    ttk.Label(frame, text="Seleccionar Tipo de Reporte:", style="Header.TLabel").pack(pady=10)

    def reporte_ventas():
        try:
            db = conectar_db()
            cursor = db.cursor()
            cursor.execute("""
                SELECT p.pedido_id, p.fecha, c.nombre, u.nombre, p.total, p.nombre_cliente_no_registrado, p.cedula_cliente_no_registrado
                FROM pedidos p
                LEFT JOIN clientes c ON p.cliente_id = c.cliente_id
                LEFT JOIN usuarios u ON p.usuario_id = u.usuario_id
            """)
            ventas = cursor.fetchall()
            db.close()

            ventana_ventas = tk.Toplevel(ventana_reportes)  # Hacer ventana_reportes el padre
            ventana_ventas.title("Reporte de Ventas")
            ventana_ventas.geometry("900x500")
            ventana_ventas.config(bg="#263238")
            ventana_ventas.transient(ventana_reportes)  # Hacer la ventana dependiente de ventana_reportes
            

            columnas = ("ID Pedido", "Fecha", "Cliente", "Empleado", "Total")
            tabla = ttk.Treeview(ventana_ventas, columns=columnas, show="headings", height=15)

            for col in columnas:
                tabla.heading(col, text=col)
                tabla.column(col, anchor="center", width=150)

            tabla.column("Fecha", width=200)
            tabla.column("Cliente", width=200)

            datos_exportar = []
            for venta in ventas:
                cliente = venta[2] if venta[2] else f"{venta[5]} (Cédula: {venta[6]})" if venta[5] else "No registrado"
                tabla.insert("", tk.END, values=(venta[0], venta[1], cliente, venta[3], venta[4]))
                datos_exportar.append((venta[0], venta[1], cliente, venta[3], venta[4]))

            tabla.pack(fill="both", expand=True, padx=10, pady=10)

            frame_exportar = ttk.Frame(ventana_ventas)
            frame_exportar.pack(fill="x", padx=10, pady=5)

            def exportar_excel():
                try:
                    if not datos_exportar:
                        messagebox.showwarning("Advertencia", "No hay datos para exportar.")
                        return
                    df = pd.DataFrame(datos_exportar, columns=columnas)
                    df.to_excel("reporte_ventas.xlsx", index=False)
                    messagebox.showinfo("Éxito", "Reporte de ventas exportado a 'reporte_ventas.xlsx'")
                except Exception as e:
                    messagebox.showerror("Error", f"No se pudo exportar a Excel: {e}")

            def exportar_pdf():
                try:
                    if not datos_exportar:
                        messagebox.showwarning("Advertencia", "No hay datos para exportar.")
                        return
                    pdf_file = "reporte_ventas.pdf"
                    doc = SimpleDocTemplate(pdf_file, pagesize=letter)
                    elements = []

                    styles = getSampleStyleSheet()
                    elements.append(Paragraph("Reporte de Ventas", styles['Title']))

                    data = [columnas]
                    for row in datos_exportar:
                        data.append([str(cell) for cell in row])

                    table = Table(data)
                    table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('FONTSIZE', (0, 0), (-1, 0), 12),
                        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                        ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ]))
                    elements.append(table)

                    doc.build(elements)
                    messagebox.showinfo("Éxito", f"Reporte de ventas exportado a '{pdf_file}'")
                except Exception as e:
                    messagebox.showerror("Error", f"No se pudo exportar a PDF: {e}")

            btn_exportar_excel = ttk.Button(frame_exportar, text="Exportar a Excel", command=exportar_excel, style="Custom.TButton")
            btn_exportar_excel.pack(side="left", padx=5)

            btn_exportar_pdf = ttk.Button(frame_exportar, text="Exportar a PDF", command=exportar_pdf, style="Custom.TButton")
            btn_exportar_pdf.pack(side="left", padx=5)

            btn_cerrar = ttk.Button(ventana_ventas, text="Cerrar", command=ventana_ventas.destroy, style="Custom.TButton")
            btn_cerrar.pack(side="bottom", padx=5)

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo generar el reporte: {e}")

    def reporte_inventario():
        try:
            db = conectar_db()
            cursor = db.cursor()
            cursor.execute("""
                SELECT p.producto_id, p.nombre, p.categoria, p.stock, p.precio, pr.nombre 
                FROM productos p
                LEFT JOIN proveedores pr ON p.proveedor_id = pr.proveedor_id
            """)
            productos = cursor.fetchall()
            db.close()

            ventana_inventario = tk.Toplevel(ventana_reportes)  # Hacer ventana_reportes el padre
            ventana_inventario.title("Reporte de Inventario")
            ventana_inventario.geometry("900x500")
            ventana_inventario.config(bg="#263238")
            ventana_inventario.transient(ventana_reportes)  # Hacer la ventana dependiente de ventana_reportes
            

            columnas = ("ID", "Nombre", "Categoría", "Stock", "Precio", "Proveedor")
            tabla = ttk.Treeview(ventana_inventario, columns=columnas, show="headings", height=15)

            for col in columnas:
                tabla.heading(col, text=col)
                tabla.column(col, anchor="center", width=120)

            tabla.column("Nombre", width=150)
            tabla.column("Categoría", width=150)
            tabla.column("Proveedor", width=150)

            datos_exportar = []
            for producto in productos:
                tabla.insert("", tk.END, values=producto)
                datos_exportar.append(producto)

            tabla.pack(fill="both", expand=True, padx=10, pady=10)

            frame_exportar = ttk.Frame(ventana_inventario)
            frame_exportar.pack(fill="x", padx=10, pady=5)

            def exportar_excel():
                try:
                    if not datos_exportar:
                        messagebox.showwarning("Advertencia", "No hay datos para exportar.")
                        return
                    df = pd.DataFrame(datos_exportar, columns=columnas)
                    df.to_excel("reporte_inventario.xlsx", index=False)
                    messagebox.showinfo("Éxito", "Reporte de inventario exportado a 'reporte_inventario.xlsx'")
                except Exception as e:
                    messagebox.showerror("Error", f"No se pudo exportar a Excel: {e}")

            def exportar_pdf():
                try:
                    if not datos_exportar:
                        messagebox.showwarning("Advertencia", "No hay datos para exportar.")
                        return
                    pdf_file = "reporte_inventario.pdf"
                    doc = SimpleDocTemplate(pdf_file, pagesize=letter)
                    elements = []

                    styles = getSampleStyleSheet()
                    elements.append(Paragraph("Reporte de Inventario", styles['Title']))

                    data = [columnas]
                    for row in datos_exportar:
                        data.append([str(cell) for cell in row])

                    table = Table(data)
                    table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('FONTSIZE', (0, 0), (-1, 0), 12),
                        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                        ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ]))
                    elements.append(table)

                    doc.build(elements)
                    messagebox.showinfo("Éxito", f"Reporte de inventario exportado a '{pdf_file}'")
                except Exception as e:
                    messagebox.showerror("Error", f"No se pudo exportar a PDF: {e}")

            btn_exportar_excel = ttk.Button(frame_exportar, text="Exportar a Excel", command=exportar_excel, style="Custom.TButton")
            btn_exportar_excel.pack(side="left", padx=5)

            btn_exportar_pdf = ttk.Button(frame_exportar, text="Exportar a PDF", command=exportar_pdf, style="Custom.TButton")
            btn_exportar_pdf.pack(side="left", padx=5)

            btn_cerrar = ttk.Button(ventana_inventario, text="Cerrar", command=ventana_inventario.destroy, style="Custom.TButton")
            btn_cerrar.pack(side="bottom", padx=5)

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo generar el reporte: {e}")

    btn_ventas = ttk.Button(frame, text="Reporte de Ventas", command=reporte_ventas, style="Custom.TButton")
    btn_ventas.pack(pady=5)

    btn_inventario = ttk.Button(frame, text="Reporte de Inventario", command=reporte_inventario, style="Custom.TButton")
    btn_inventario.pack(pady=5)

    btn_cerrar = ttk.Button(frame, text="Cerrar", 
                           command=lambda: cerrar_ventana_secundaria(ventana_reportes, ventana_principal), 
                           style="Custom.TButton")
    btn_cerrar.pack(pady=10)