import tkinter as tk
from tkinter import ttk, messagebox
import sys
import bcrypt
import config
from styles import aplicar_estilo, aplicar_estilo_login
from database import conectar_db
from business_logic import consultar_productos, agregar_producto, gestionar_proveedores, gestionar_clientes, gestionar_empleados, registrar_venta, generar_reportes
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Variables globales

MAX_INTENTOS = 3
global intentos_login
intentos_login = 0


# Añadir después de las importaciones en ui.py
class Tooltip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip_window = None
        self.id = None

    def show(self):
        if self.tooltip_window or not self.text:
            return
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 25
        self.tooltip_window = tk.Toplevel(self.widget)
        self.tooltip_window.wm_overrideredirect(True)  # Sin bordes ni barra de título
        self.tooltip_window.wm_geometry(f"+{x}+{y}")
        label = tk.Label(self.tooltip_window, text=self.text, justify="left",
                         background="#FFFF99", relief="solid", borderwidth=1,
                         font=("Helvetica", 10))
        label.pack()

    def hide(self):
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None

def cerrar_ventana(ventana):
    ventana.quit()  # Termina el bucle principal
    ventana.destroy()

# Función para la ventana de inicio de sesión
def ventana_inicio_sesion(ventana_raiz):
    global intentos_login
    intentos_login = 0

    login_window = tk.Toplevel(ventana_raiz)
    login_window.title("Inicio de Sesión")
    login_window.protocol("WM_DELETE_WINDOW", lambda: cerrar_ventana(login_window))  # Cerrar la ventana de login 
    login_window.config(bg="#263238")  # Configurar el fondo de la ventana de inicio de sesión

    ventana_ancho = 350
    ventana_alto = 250
    pantalla_ancho = login_window.winfo_screenwidth()
    pantalla_alto = login_window.winfo_screenheight()
    x = (pantalla_ancho // 2) - (ventana_ancho // 2)
    y = (pantalla_alto // 2) - (ventana_alto // 2)
    login_window.geometry(f"{ventana_ancho}x{ventana_alto}+{x}+{y}")

    aplicar_estilo_login()

    frame = ttk.Frame(login_window)
    frame.pack(padx=20, pady=20, fill="both", expand=True)

    header_label = ttk.Label(frame, text="Inicio de Sesión", style="Header.TLabel")
    header_label.pack(pady=(0, 10))

    ttk.Label(frame, text="Usuario:").pack()
    entry_usuario = ttk.Entry(frame)
    entry_usuario.pack(fill="x", pady=5)
    entry_usuario.delete(0, tk.END)

    ttk.Label(frame, text="Contraseña:").pack()
    entry_contrasena = ttk.Entry(frame, show="*")
    entry_contrasena.pack(fill="x", pady=5)
    entry_contrasena.delete(0, tk.END)

    label_intentos = ttk.Label(frame, text=f"Intentos restantes: {MAX_INTENTOS - intentos_login}")
    label_intentos.pack(pady=5)

    frame_botones = ttk.Frame(frame)
    frame_botones.pack(fill="x", pady=10)

    def iniciar_sesion():
        global intentos_login
        username = entry_usuario.get().strip()
        password = entry_contrasena.get().strip()

        if not username or not password:
            messagebox.showwarning("Advertencia", "Por favor, ingresa usuario y contraseña.")
            return

        try:
            db = conectar_db()
            cursor = db.cursor()
            cursor.execute("SELECT password, rol FROM usuarios WHERE username = %s", (username,))
            resultado = cursor.fetchone()
            db.close()

            if resultado:
                stored_password = resultado[0]
                rol = resultado[1]

                if bcrypt.checkpw(password.encode('utf-8'), stored_password.encode('utf-8')):
                    config.usuario_rol = rol
                    print(f"Rol asignado: {config.usuario_rol}")
                    messagebox.showinfo("Éxito", f"Bienvenido, {username} ({rol})")
                    login_window.destroy()
                    ventana_raiz.deiconify()
                    mostrar_ventana_principal(ventana_raiz)
                else:
                    intentos_login += 1
                    if intentos_login >= MAX_INTENTOS:
                        messagebox.showerror("Error", "Has alcanzado el máximo de intentos. El programa se cerrará.")
                        login_window.destroy()
                        sys.exit()
                    messagebox.showerror("Error", "Usuario o contraseña incorrectos.")
                    label_intentos.config(text=f"Intentos restantes: {MAX_INTENTOS - intentos_login}")
            else:
                intentos_login += 1
                if intentos_login >= MAX_INTENTOS:
                    messagebox.showerror("Error", "Has alcanzado el máximo de intentos. El programa se cerrará.")
                    login_window.destroy()
                    sys.exit()
                messagebox.showerror("Error", "Usuario o contraseña incorrectos.")
                label_intentos.config(text=f"Intentos restantes: {MAX_INTENTOS - intentos_login}")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo iniciar sesión: {e}")
    
    
    def salir_programa():
        print("Saliendo del programa...")
        login_window.destroy()
        sys.exit()

    btn_login = ttk.Button(frame_botones, text="Iniciar Sesión", command=iniciar_sesion, style="Custom.TButton")
    btn_login.pack(side="left", padx=5)

    btn_salir = ttk.Button(frame_botones, text="Salir", command=salir_programa, style="Custom.TButton")
    btn_salir.pack(side="right", padx=5)

# Función para mostrar la ventana principal
def mostrar_ventana_principal(ventana_raiz):
    print("Rol asignado:", config.usuario_rol)  # Imprimir el rol del usuario
    for widget in ventana_raiz.winfo_children():
        widget.destroy()

    ventana_raiz.title("Gestión de Inventario")
    ventana_raiz.config(bg="#263238")  # Fondo gris oscuro
    ventana_raiz.protocol("WM_DELETE_WINDOW", lambda: cerrar_ventana(ventana_raiz))  # Cerrar la ventana principal

    ventana_ancho = 600
    ventana_alto = 500
    pantalla_ancho = ventana_raiz.winfo_screenwidth()
    pantalla_alto = ventana_raiz.winfo_screenheight()
    x = (pantalla_ancho // 2) - (ventana_ancho // 2)
    y = (pantalla_alto // 2) - (ventana_alto // 2)
    ventana_raiz.geometry(f"{ventana_ancho}x{ventana_alto}+{x}+{y}")
   

    aplicar_estilo()

    frame_principal = ttk.Frame(ventana_raiz)
    frame_principal.pack(fill="both", expand=True)

    sidebar_frame = ttk.Frame(frame_principal, style="Sidebar.TFrame")
    sidebar_frame.pack(side="left", fill="y", padx=0, pady=0)

    content_frame = ttk.Frame(frame_principal)
    content_frame.pack(side="right", fill="both", expand=True, padx=20, pady=20)

    header_label = ttk.Label(content_frame, text="Gestión de Inventario", style="Header.TLabel")
    header_label.pack(pady=(0, 20))

    summary_frame = ttk.LabelFrame(content_frame, text="Resumen", padding=10, style="Header.TFrame")
    summary_frame.pack(fill="x", pady=10)
    summary_frame.pack(fill="both", expand=True)

    canvas_widget = actualizar_resumen(summary_frame)

    btn_actualizar = ttk.Button(content_frame, text="Actualizar Resumen", command=lambda: actualizar_resumen(summary_frame, canvas_widget), style="Custom.TButton")
    btn_actualizar.pack(pady=10)

    btn_consultar_productos = ttk.Button(sidebar_frame, text="Consultar Productos", command=consultar_productos, style="Custom.TButton")
    btn_consultar_productos.pack(pady=5, padx=10)

    btn_agregar_producto = ttk.Button(sidebar_frame, text="Agregar Producto", command=agregar_producto, style="Custom.TButton")
    btn_agregar_producto.pack(pady=5, padx=10)

    btn_gestionar_proveedores = ttk.Button(sidebar_frame, text="Gestionar Proveedores", command=gestionar_proveedores, style="Custom.TButton")
    btn_gestionar_proveedores.pack(pady=5, padx=10)

    btn_gestionar_clientes = ttk.Button(sidebar_frame, text="Gestionar Clientes", command=gestionar_clientes, style="Custom.TButton")
    btn_gestionar_clientes.pack(pady=5, padx=10)

    btn_gestionar_empleados = ttk.Button(sidebar_frame, text="Gestionar Empleados", command=gestionar_empleados, style="Custom.TButton")
    btn_gestionar_empleados.pack(pady=5, padx=10)

    btn_registrar_venta = ttk.Button(sidebar_frame, text="Registrar Venta", command=registrar_venta, style="Custom.TButton")
    btn_registrar_venta.pack(pady=5, padx=10)

    btn_generar_reportes = ttk.Button(sidebar_frame, text="Generar Reportes", command=generar_reportes, style="Custom.TButton")
    btn_generar_reportes.pack(pady=5, padx=10)

    separator = ttk.Separator(sidebar_frame, orient="horizontal")
    separator.pack(fill="x", pady=10, padx=10)

    btn_cerrar_sesion = ttk.Button(sidebar_frame, text="Cerrar Sesión", command=lambda: cerrar_sesion(ventana_raiz), style="Custom.TButton")
    btn_cerrar_sesion.pack(pady=5, padx=10)

    def cerrar_sesion(ventana_raiz):
        if messagebox.askyesno("Confirmar", "¿Estás seguro de que deseas cerrar sesión?"):
            for widget in ventana_raiz.winfo_children():
                widget.destroy()
            ventana_raiz.withdraw()
            ventana_inicio_sesion(ventana_raiz)

# Reemplazar la función actualizar_resumen en ui.py
def actualizar_resumen(summary_frame, canvas_widget=None):
    try:
        db = conectar_db()
        cursor = db.cursor()

        # Total de productos
        cursor.execute("SELECT COUNT(*) FROM productos")
        total_productos = cursor.fetchone()[0]

        # Stock total
        cursor.execute("SELECT SUM(stock) FROM productos")
        total_stock = cursor.fetchone()[0] or 0

        # Total de ventas
        cursor.execute("SELECT COUNT(*) FROM pedidos")
        total_ventas = cursor.fetchone()[0]

        # Total de ingresos
        cursor.execute("SELECT SUM(total) FROM pedidos")
        total_ingresos = cursor.fetchone()[0] or 0.0

        # Productos con bajo stock (stock < 5) - Obtener detalles
        cursor.execute("SELECT nombre, stock FROM productos WHERE stock < 5")
        productos_bajo_stock = cursor.fetchall()
        bajo_stock = len(productos_bajo_stock)

        # Crear el texto para el tooltip
        if bajo_stock > 0:
            tooltip_text = "\n".join([f"{nombre}: {stock} unidades" for nombre, stock in productos_bajo_stock])
        else:
            tooltip_text = "No hay productos con bajo stock."

        # Última venta (fecha y monto)
        cursor.execute("SELECT fecha, total FROM pedidos ORDER BY fecha DESC LIMIT 1")
        ultima_venta = cursor.fetchone()
        if ultima_venta:
            fecha_ultima_venta, monto_ultima_venta = ultima_venta
        else:
            fecha_ultima_venta, monto_ultima_venta = "N/A", 0.0

        # Datos para el gráfico: Número de ventas por día
        cursor.execute("SELECT DATE(fecha) as fecha, COUNT(*) as num_ventas FROM pedidos GROUP BY DATE(fecha) ORDER BY num_ventas DESC")
        ventas_por_dia = cursor.fetchall()

        db.close()

        # Limpiar el contenido actual del summary_frame
        for widget in summary_frame.winfo_children():
            widget.destroy()

        # Frame para las métricas
        metrics_frame = ttk.Frame(summary_frame, style="Summary.TFrame")
        metrics_frame.pack(fill="x", pady=5)

        # Mostrar las métricas con emojis y separadores
        ttk.Label(metrics_frame, text=f"📦 Total de Productos: {total_productos}", style="Summary.TLabel", background="#263238").pack(anchor="w", padx=10, pady=2)
        ttk.Separator(metrics_frame, orient="horizontal").pack(fill="x", pady=5)
        ttk.Label(metrics_frame, text=f"📏 Stock Total: {total_stock}", style="Summary.TLabel", background="#263238").pack(anchor="w", padx=10, pady=2)
        ttk.Separator(metrics_frame, orient="horizontal").pack(fill="x", pady=5)
        ttk.Label(metrics_frame, text=f"🛒 Total de Ventas: {total_ventas}", style="Summary.TLabel", background="#263238").pack(anchor="w", padx=10, pady=2)
        ttk.Separator(metrics_frame, orient="horizontal").pack(fill="x", pady=5)
        ttk.Label(metrics_frame, text=f"💰 Total de Ingresos: ${total_ingresos:.2f}", style="Summary.TLabel", background="#263238").pack(anchor="w", padx=10, pady=2)
        ttk.Separator(metrics_frame, orient="horizontal").pack(fill="x", pady=5)

        # Etiqueta de productos con bajo stock con tooltip
        bajo_stock_label = ttk.Label(metrics_frame, text=f"⚠️ Productos con Bajo Stock: {bajo_stock}", style="Summary.TLabel", background="#263238")
        bajo_stock_label.pack(anchor="w", padx=10, pady=2)

        # Crear el tooltip y vincularlo a los eventos
        tooltip = Tooltip(bajo_stock_label, tooltip_text)
        bajo_stock_label.bind("<Enter>", lambda e: tooltip.show())
        bajo_stock_label.bind("<Leave>", lambda e: tooltip.hide())

        # Etiqueta de última venta
        ttk.Separator(metrics_frame, orient="horizontal").pack(fill="x", pady=5)
        ttk.Label(metrics_frame, text=f"🕒 Última Venta: {fecha_ultima_venta} - ${monto_ultima_venta:.2f}", style="Summary.TLabel", background="#263238").pack(anchor="w", padx=10, pady=2)

        # Frame para el gráfico
        chart_frame = ttk.Frame(summary_frame)
        chart_frame.pack(fill="both", expand=True, pady=10)

        # Crear el gráfico de número de ventas por día
        fig, ax = plt.subplots(figsize=(5, 2), dpi=100)
        fig.patch.set_facecolor('#263238')  
        ax.set_facecolor('#37474F')
        if ventas_por_dia:
            fechas = [str(row[0]) for row in ventas_por_dia]
            num_ventas = [row[1] for row in ventas_por_dia]

            # Crear una lista de colores: el día con más ventas (primera barra) será #42A5F5, las demás #1976D2
            colores = ["#42A5F5" if i == 0 else "#1976D2" for i in range(len(fechas))]

            # Generar el gráfico con colores diferenciados
            ax.bar(fechas, num_ventas, color=colores)
            ax.set_title("Número de Ventas por Día", fontsize=10, color="#0D47A1")
            ax.set_xlabel("Fecha", fontsize=8)
            ax.set_ylabel("Número de Ventas", fontsize=8)
            plt.xticks(rotation=45, fontsize=6)
            plt.yticks(fontsize=6)
            plt.tight_layout()
        else:
            ax.text(0.5, 0.5, "No hay datos de ventas", horizontalalignment="center", verticalalignment="center", fontsize=10)
            ax.set_xticks([])
            ax.set_yticks([])

        # Si ya existe un canvas, destruirlo para evitar superposición
        if canvas_widget:
            canvas_widget.destroy()

        # Integrar el gráfico en Tkinter
        canvas = FigureCanvasTkAgg(fig, master=chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

        return canvas.get_tk_widget()

    except Exception as e:
        messagebox.showerror("Error", f"No se pudo actualizar el resumen: {e}")
        return None