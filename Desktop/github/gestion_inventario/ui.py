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

# Función para la ventana de inicio de sesión
def ventana_inicio_sesion(ventana_raiz):
    global intentos_login
    intentos_login = 0

    login_window = tk.Toplevel(ventana_raiz)
    login_window.title("Inicio de Sesión")
    login_window.protocol("WM_DELETE_WINDOW", lambda: cerrar_ventana(login_window))
    login_window.config(bg="#263238")

    ventana_ancho = 350
    ventana_alto = 300  # Aumentado para acomodar el nuevo botón
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

    # Crear frame para contraseña y su ícono de información
    frame_password = ttk.Frame(frame)
    frame_password.pack(fill="x", pady=0)

    # Ícono de información
    info_label = ttk.Label(frame_password, text="ℹ️", cursor="hand2")
    info_label.pack(side="left", padx=5)

    # Crear tooltip para los requisitos de contraseña
    requisitos_texto = ("La contraseña debe tener:\n" +
                      "• Mínimo 8 caracteres\n" +
                      "• Una letra mayúscula\n" +
                      "• Una letra minúscula\n" +
                      "• Un número\n" +
                      "• Un carácter especial")
    
    tooltip_requisitos = Tooltip(info_label, requisitos_texto)
    info_label.bind("<Enter>", lambda e: tooltip_requisitos.show())
    info_label.bind("<Leave>", lambda e: tooltip_requisitos.hide())

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
            cursor.execute("SELECT usuario_id, password, rol, nombre FROM usuarios WHERE username = %s", (username,))
            resultado = cursor.fetchone()
            db.close()

            if resultado:
                usuario_id, stored_password, rol, nombre = resultado
                if bcrypt.checkpw(password.encode('utf-8'), stored_password.encode('utf-8')):
                    config.usuario_rol = rol
                    config.usuario_id = usuario_id
                    config.usuario_nombre = nombre
                    print(f"Rol asignado: {config.usuario_rol}")
                    print(f"Usuario ID: {config.usuario_id}")
                    print(f"Nombre: {config.usuario_nombre}")
                    messagebox.showinfo("Éxito", f"Bienvenido, {nombre} ({rol})")
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

    btn_registro = ttk.Button(frame_botones, text="Registrarse", command=lambda: ventana_registro(ventana_raiz), style="Custom.TButton")
    btn_registro.pack(side="left", padx=5)

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

    # Frame para el resumen con estilo mejorado
    summary_frame = ttk.LabelFrame(content_frame, text="📊 Resumen del Sistema", padding=15, style="Header.TFrame")
    summary_frame.pack(fill="both", expand=True, padx=20, pady=15)

    # Frame interno para el contenido del resumen
    summary_content = ttk.Frame(summary_frame, style="Summary.TFrame")
    summary_content.pack(fill="both", expand=True, padx=10, pady=10)

    # Título del resumen con estilo mejorado
    summary_title = ttk.Label(summary_content, 
                            text="Estado Actual del Inventario", 
                            style="Header.TLabel",
                            font=("Helvetica", 14, "bold"))
    summary_title.pack(pady=(0, 15))

    # Frame para las métricas con estilo de tarjetas
    metrics_frame = ttk.Frame(summary_content, style="Summary.TFrame")
    metrics_frame.pack(fill="x", pady=5)

    # Estilo para las métricas
    style = ttk.Style()
    style.configure("Metric.TLabel", 
                   font=("Helvetica", 11),
                   padding=10,
                   background="#37474F",
                   foreground="#E0E0E0")

    style.configure("Metric.TFrame",
                   background="#37474F",
                   relief="raised",
                   borderwidth=1)

    # Función para crear una tarjeta métrica
    def create_metric_card(parent, icon, title, value, tooltip=None):
        frame = ttk.Frame(parent, style="Metric.TFrame")
        frame.pack(side="left", fill="x", expand=True, padx=5, pady=5)
        
        # Ícono y título en la misma línea
        icon_label = ttk.Label(frame, text=icon, font=("Helvetica", 16), foreground="#E0E0E0", background="#37474F")
        icon_label.pack(side="left", padx=5)
        
        title_label = ttk.Label(frame, text=title, style="Metric.TLabel", background="#37474F")
        title_label.pack(side="left", padx=5)
        
        value_label = ttk.Label(frame, text=value, font=("Helvetica", 16, "bold"), foreground="#E0E0E0", background="#37474F")
        value_label.pack(side="right", padx=5)
        
        if tooltip:
            tooltip_obj = Tooltip(frame, tooltip)
            frame.bind("<Enter>", lambda e: tooltip_obj.show())
            frame.bind("<Leave>", lambda e: tooltip_obj.hide())
        
        return value_label

    # Crear las tarjetas de métricas con referencias a los labels
    total_productos_label = create_metric_card(metrics_frame, "📦", "Total Productos", "0")
    stock_total_label = create_metric_card(metrics_frame, "📏", "Stock Total", "0")
    total_ventas_label = create_metric_card(metrics_frame, "🛒", "Total Ventas", "0")
    total_ingresos_label = create_metric_card(metrics_frame, "💰", "Total Ingresos", "$0.00")
    bajo_stock_label = create_metric_card(metrics_frame, "⚠️", "Bajo Stock", "0", "Productos con stock bajo")

    # Separador con estilo
    separator = ttk.Separator(summary_content, orient="horizontal")
    separator.pack(fill="x", pady=15)

    # Frame para el gráfico
    chart_frame = ttk.LabelFrame(summary_content, text="📈 Gráfico de Ventas", padding=10, style="Dark.TLabelframe")
    chart_frame.pack(fill="both", expand=True, pady=10)

    # Configurar el estilo del frame
    style = ttk.Style()
    style.configure("Dark.TLabelframe", background="#263238", foreground="#E0E0E0")
    style.configure("Dark.TLabelframe.Label", background="#263238", foreground="#E0E0E0")

    # Botón de actualización con estilo mejorado
    btn_actualizar = ttk.Button(summary_content, 
                               text="🔄 Actualizar Resumen", 
                               command=lambda: actualizar_resumen(summary_frame),
                               style="Custom.TButton")
    btn_actualizar.pack(pady=15)

    # Primera actualización del resumen
    actualizar_resumen(summary_frame)

    btn_consultar_productos = ttk.Button(sidebar_frame, text="Consultar Productos", 
                                       command=lambda: consultar_productos(ventana_raiz), 
                                       style="Custom.TButton")
    btn_consultar_productos.pack(pady=5, padx=10)

    btn_agregar_producto = ttk.Button(sidebar_frame, text="Agregar Producto", 
                                     command=lambda: agregar_producto(ventana_raiz), 
                                     style="Custom.TButton")
    btn_agregar_producto.pack(pady=5, padx=10)

    btn_gestionar_proveedores = ttk.Button(sidebar_frame, text="Gestionar Proveedores", 
                                          command=lambda: gestionar_proveedores(ventana_raiz), 
                                          style="Custom.TButton")
    btn_gestionar_proveedores.pack(pady=5, padx=10)

    btn_gestionar_clientes = ttk.Button(sidebar_frame, text="Gestionar Clientes", 
                                       command=lambda: gestionar_clientes(ventana_raiz), 
                                       style="Custom.TButton")
    btn_gestionar_clientes.pack(pady=5, padx=10)

    btn_gestionar_empleados = ttk.Button(sidebar_frame, text="Gestionar Empleados", 
                                        command=lambda: gestionar_empleados(ventana_raiz), 
                                        style="Custom.TButton")
    btn_gestionar_empleados.pack(pady=5, padx=10)

    btn_registrar_venta = ttk.Button(sidebar_frame, text="Registrar Venta", 
                                    command=lambda: registrar_venta(ventana_raiz), 
                                    style="Custom.TButton")
    btn_registrar_venta.pack(pady=5, padx=10)

    btn_generar_reportes = ttk.Button(sidebar_frame, text="Generar Reportes", 
                                     command=lambda: generar_reportes(ventana_raiz), 
                                     style="Custom.TButton")
    btn_generar_reportes.pack(pady=5, padx=10)

    separator = ttk.Separator(sidebar_frame, orient="horizontal")
    separator.pack(fill="x", pady=10, padx=10)

    btn_cerrar_sesion = ttk.Button(sidebar_frame, text="Cerrar Sesión", 
                                  command=lambda: cerrar_sesion(ventana_raiz), 
                                  style="Custom.TButton")
    btn_cerrar_sesion.pack(pady=5, padx=10)

    def cerrar_sesion(ventana_raiz):
        if messagebox.askyesno("Confirmar", "¿Estás seguro de que deseas cerrar sesión?"):
            for widget in ventana_raiz.winfo_children():
                widget.destroy()
            ventana_raiz.withdraw()
            ventana_inicio_sesion(ventana_raiz)

def actualizar_resumen(summary_frame):
    try:
        print("Iniciando actualización del resumen...")
        db = conectar_db()
        cursor = db.cursor()

        # Total de productos
        cursor.execute("SELECT COUNT(*) FROM productos")
        total_productos = cursor.fetchone()[0]
        print(f"Total productos: {total_productos}")

        # Stock total
        cursor.execute("SELECT SUM(stock) FROM productos")
        total_stock = cursor.fetchone()[0] or 0
        print(f"Total stock: {total_stock}")

        # Total de ventas
        cursor.execute("SELECT COUNT(*) FROM pedidos")
        total_ventas = cursor.fetchone()[0]
        print(f"Total ventas: {total_ventas}")

        # Total de ingresos
        cursor.execute("SELECT SUM(total) FROM pedidos")
        total_ingresos = cursor.fetchone()[0] or 0.0
        print(f"Total ingresos: {total_ingresos}")

        # Productos con bajo stock (stock < 5)
        cursor.execute("SELECT nombre, stock FROM productos WHERE stock < 5")
        productos_bajo_stock = cursor.fetchall()
        bajo_stock = len(productos_bajo_stock)
        print(f"Productos con bajo stock: {bajo_stock}")

        # Buscar el frame de contenido del resumen
        summary_content = None
        for widget in summary_frame.winfo_children():
            if isinstance(widget, ttk.Frame):
                summary_content = widget
                break

        if not summary_content:
            print("No se encontró el frame de contenido del resumen")
            return

        # Buscar el frame de métricas
        metrics_frame = None
        for widget in summary_content.winfo_children():
            if isinstance(widget, ttk.Frame) and len(widget.winfo_children()) > 0:
                # Verificar si este frame contiene las métricas
                first_child = widget.winfo_children()[0]
                if isinstance(first_child, ttk.Frame):
                    metrics_frame = widget
                    break

        if not metrics_frame:
            print("No se encontró el frame de métricas")
            return

        print("Frame de métricas encontrado")

        # Actualizar cada métrica
        for metric_frame in metrics_frame.winfo_children():
            if not isinstance(metric_frame, ttk.Frame):
                continue

            # Buscar el título y el valor en este frame
            title_label = None
            value_label = None
            
            for label in metric_frame.winfo_children():
                if isinstance(label, ttk.Label):
                    if "Total Productos" in label.cget("text"):
                        value_label = metric_frame.winfo_children()[-1]  # El último label es el valor
                        value_label.configure(text=str(total_productos))
                        print(f"Actualizado Total Productos: {total_productos}")
                        break
                    elif "Stock Total" in label.cget("text"):
                        value_label = metric_frame.winfo_children()[-1]
                        value_label.configure(text=str(total_stock))
                        print(f"Actualizado Stock Total: {total_stock}")
                        break
                    elif "Total Ventas" in label.cget("text"):
                        value_label = metric_frame.winfo_children()[-1]
                        value_label.configure(text=str(total_ventas))
                        print(f"Actualizado Total Ventas: {total_ventas}")
                        break
                    elif "Total Ingresos" in label.cget("text"):
                        value_label = metric_frame.winfo_children()[-1]
                        value_label.configure(text=f"${total_ingresos:,.2f}")
                        print(f"Actualizado Total Ingresos: ${total_ingresos:,.2f}")
                        break
                    elif "Bajo Stock" in label.cget("text"):
                        value_label = metric_frame.winfo_children()[-1]
                        value_label.configure(text=str(bajo_stock))
                        print(f"Actualizado Bajo Stock: {bajo_stock}")
                        break

        # Actualizar el gráfico
        chart_frame = None
        for widget in summary_content.winfo_children():
            if isinstance(widget, ttk.LabelFrame) and "Gráfico de Ventas" in widget.cget("text"):
                chart_frame = widget
                break

        if chart_frame:
            print("Actualizando gráfico...")
            # Limpiar el frame del gráfico
            for widget in chart_frame.winfo_children():
                widget.destroy()

            # Datos para el gráfico
            cursor.execute("""
                SELECT DATE(fecha) as fecha, COUNT(*) as num_ventas 
                FROM pedidos 
                GROUP BY DATE(fecha) 
                ORDER BY fecha DESC 
                LIMIT 7
            """)
            ventas_por_dia = cursor.fetchall()
            print(f"Datos de ventas obtenidos: {ventas_por_dia}")

            # Crear el gráfico
            fig, ax = plt.subplots(figsize=(5, 2), dpi=100)
            fig.patch.set_facecolor('#263238')
            ax.set_facecolor('#263238')

            if ventas_por_dia:
                fechas = [str(row[0]) for row in ventas_por_dia]
                num_ventas = [row[1] for row in ventas_por_dia]
                print(f"Fechas: {fechas}")
                print(f"Número de ventas: {num_ventas}")

                # Crear una lista de colores con tonos más suaves
                colores = ["#64B5F6" if i == 0 else "#2196F3" for i in range(len(fechas))]

                # Generar el gráfico
                ax.bar(fechas, num_ventas, color=colores)
                ax.set_title("Número de Ventas por Día", fontsize=10, color="#E0E0E0")
                ax.set_xlabel("Fecha", fontsize=8, color="#E0E0E0")
                ax.set_ylabel("Número de Ventas", fontsize=8, color="#E0E0E0")
                plt.xticks(rotation=45, fontsize=6, color="#E0E0E0")
                plt.yticks(fontsize=6, color="#E0E0E0")
                
                # Agregar grid con color suave
                ax.grid(True, linestyle='--', alpha=0.3, color='#E0E0E0')
                
                plt.tight_layout()
                print("Gráfico generado con datos")
            else:
                ax.text(0.5, 0.5, "No hay datos de ventas", 
                       horizontalalignment="center", 
                       verticalalignment="center", 
                       fontsize=10,
                       color="#E0E0E0")
                ax.set_xticks([])
                ax.set_yticks([])
                print("No hay datos para el gráfico")

            # Integrar el gráfico en Tkinter
            canvas = FigureCanvasTkAgg(fig, master=chart_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True)
            print("Gráfico integrado en la interfaz")

        db.close()
        print("Actualización del resumen completada")

    except Exception as e:
        messagebox.showerror("Error", f"No se pudo actualizar el resumen: {e}")
        print(f"Error en actualizar_resumen: {e}")
        # Para debugging más detallado
        import traceback
        traceback.print_exc()

def ventana_registro(ventana_raiz):
    registro_window = tk.Toplevel(ventana_raiz)
    registro_window.title("Registro de Usuario")
    registro_window.protocol("WM_DELETE_WINDOW", lambda: cerrar_ventana_secundaria(registro_window, ventana_raiz))
    registro_window.config(bg="#263238")

    ventana_ancho = 400
    ventana_alto = 550  # Aumentado para el nuevo campo
    pantalla_ancho = registro_window.winfo_screenwidth()
    pantalla_alto = registro_window.winfo_screenheight()
    x = (pantalla_ancho // 2) - (ventana_ancho // 2)
    y = (pantalla_alto // 2) - (ventana_alto // 2)
    registro_window.geometry(f"{ventana_ancho}x{ventana_alto}+{x}+{y}")

    aplicar_estilo_login()

    frame = ttk.Frame(registro_window)
    frame.pack(padx=20, pady=20, fill="both", expand=True)

    header_label = ttk.Label(frame, text="Registro de Usuario", style="Header.TLabel")
    header_label.pack(pady=(0, 10))

    ttk.Label(frame, text="Nombre Completo:").pack()
    entry_nombre = ttk.Entry(frame)
    entry_nombre.pack(fill="x", pady=5)

    ttk.Label(frame, text="Nombre de Usuario:").pack()
    entry_usuario = ttk.Entry(frame)
    entry_usuario.pack(fill="x", pady=5)

    ttk.Label(frame, text="Correo Electrónico:").pack()
    entry_correo = ttk.Entry(frame)
    entry_correo.pack(fill="x", pady=5)

    ttk.Label(frame, text="Contraseña:").pack()
    entry_contrasena = ttk.Entry(frame, show="*")
    entry_contrasena.pack(fill="x", pady=5)

    # Crear frame para contraseña y su ícono de información
    frame_password = ttk.Frame(frame)
    frame_password.pack(fill="x", pady=0)

    # Ícono de información
    info_label = ttk.Label(frame_password, text="ℹ️", cursor="hand2")
    info_label.pack(side="left", padx=5)

    # Crear tooltip para los requisitos de contraseña
    requisitos_texto = ("La contraseña debe tener:\n" +
                      "• Mínimo 8 caracteres\n" +
                      "• Una letra mayúscula\n" +
                      "• Una letra minúscula\n" +
                      "• Un número\n" +
                      "• Un carácter especial")
    
    tooltip_requisitos = Tooltip(info_label, requisitos_texto)
    info_label.bind("<Enter>", lambda e: tooltip_requisitos.show())
    info_label.bind("<Leave>", lambda e: tooltip_requisitos.hide())

    ttk.Label(frame, text="Confirmar Contraseña:").pack()
    entry_confirmar = ttk.Entry(frame, show="*")
    entry_confirmar.pack(fill="x", pady=5)

    ttk.Label(frame, text="Rol:").pack()
    rol_var = tk.StringVar(value="empleado")
    frame_roles = ttk.Frame(frame)
    frame_roles.pack(fill="x", pady=5)
    
    ttk.Radiobutton(frame_roles, text="Administrador", variable=rol_var, value="admin").pack(side="left", padx=5)
    ttk.Radiobutton(frame_roles, text="Empleado", variable=rol_var, value="empleado").pack(side="left", padx=5)

    def validar_contraseña(password):
        if len(password) < 8:
            return False, "La contraseña debe tener al menos 8 caracteres"
        if not any(c.isupper() for c in password):
            return False, "La contraseña debe contener al menos una letra mayúscula"
        if not any(c.islower() for c in password):
            return False, "La contraseña debe contener al menos una letra minúscula"
        if not any(c.isdigit() for c in password):
            return False, "La contraseña debe contener al menos un número"
        if not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
            return False, "La contraseña debe contener al menos un carácter especial"
        return True, ""

    def validar_correo(correo):
        import re
        patron = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(patron, correo))

    def registrar_usuario():
        nombre = entry_nombre.get().strip()
        username = entry_usuario.get().strip()
        correo = entry_correo.get().strip()
        password = entry_contrasena.get().strip()
        confirmar = entry_confirmar.get().strip()
        rol = rol_var.get()

        if not nombre or not username or not correo or not password or not confirmar:
            messagebox.showwarning("Advertencia", "Por favor, complete todos los campos.")
            return

        if not validar_correo(correo):
            messagebox.showwarning("Advertencia", "Por favor, ingrese un correo electrónico válido.")
            return

        es_valida, mensaje = validar_contraseña(password)
        if not es_valida:
            messagebox.showwarning("Advertencia", mensaje)
            return

        if password != confirmar:
            messagebox.showwarning("Advertencia", "Las contraseñas no coinciden.")
            return

        try:
            db = conectar_db()
            cursor = db.cursor()
            
            # Verificar si el usuario ya existe
            cursor.execute("SELECT username FROM usuarios WHERE username = %s", (username,))
            if cursor.fetchone():
                messagebox.showerror("Error", "El nombre de usuario ya existe.")
                return

            # Verificar si el correo ya existe
            cursor.execute("SELECT email FROM usuarios WHERE email = %s", (correo,))
            if cursor.fetchone():
                messagebox.showerror("Error", "El correo electrónico ya está registrado.")
                return

            # Hashear la contraseña
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            
            # Insertar el nuevo usuario
            cursor.execute(
                "INSERT INTO usuarios (username, nombre, email, password, rol) VALUES (%s, %s, %s, %s, %s)",
                (username, nombre, correo, hashed_password, rol)
            )
            db.commit()
            db.close()

            messagebox.showinfo("Éxito", "Usuario registrado exitosamente.")
            registro_window.destroy()

        except Exception as e:
            messagebox.showerror("Error", f"Error al registrar usuario: {e}")

    frame_botones = ttk.Frame(frame)
    frame_botones.pack(fill="x", pady=10)

    btn_registrar = ttk.Button(frame_botones, text="Registrar", command=registrar_usuario, style="Custom.TButton")
    btn_registrar.pack(side="left", padx=5)

    btn_cancelar = ttk.Button(frame_botones, text="Cancelar", command=registro_window.destroy, style="Custom.TButton")
    btn_cancelar.pack(side="right", padx=5)