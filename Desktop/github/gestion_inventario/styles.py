from tkinter import ttk

def aplicar_estilo():
    estilo = ttk.Style()
    estilo.theme_use("clam")  # Usamos el tema clam para los widgets de ttk

    # Estilo de los botones
    estilo.configure("Custom.TButton", 
                     background="#37474F",  # Usamos un color gris oscuro
                     foreground="white", 
                     font=("Helvetica", 10, "bold"),
                     padding=8,
                     borderwidth=0,
                     width=20)
    estilo.map("Custom.TButton",
               background=[("active", "#455A64"), ("!active", "#37474F"), ("hover", "#546E7A")],
               foreground=[("active", "white"), ("hover", "white")])

    # Fondo de los frames
    estilo.configure("TFrame", background="#263238")  # Fondo gris oscuro
    estilo.configure("Sidebar.TFrame", background="#1C313A")  # Fondo más oscuro para la barra lateral
    estilo.configure("Summary.TFrame", background="#263238")  # Fondo gris azulado
    estilo.configure("TLabelFrame", background="#263238")  # Fondo oscuro
    estilo.configure("TLabelFrame.Label", background="#263238", font=("Helvetica", 12, "bold"))

    # Estilo de las etiquetas
    estilo.configure("TLabel", background="#263238", font=("Helvetica", 11), foreground="#FFFFFF")

    # Estilo para el encabezado
    estilo.configure("Header.TLabel", background="#263238", font=("Helvetica", 16, "bold"), foreground="#64B5F6")  # Color azul claro

    # Estilo para las etiquetas del panel de resumen
    estilo.configure("Summary.TLabel", background="#2C3E50", font=("Helvetica", 11), foreground="#B0BEC5")  # Gris claro

    # Estilo del Treeview
    estilo.configure("Treeview", 
                     background="#37474F",  # Fondo oscuro para el Treeview
                     foreground="white", 
                     rowheight=25, 
                     fieldbackground="#263238")  # Fondo oscuro en el Treeview
    estilo.configure("Treeview.Heading", 
                     background="#455A64",  # Fondo gris oscuro para el encabezado
                     foreground="white", 
                     font=("Helvetica", 10, "bold"))
    estilo.map("Treeview", 
               background=[("selected", "#64B5F6")],  # Azul claro cuando se selecciona
               foreground=[("selected", "black")])

def aplicar_estilo_login():
    estilo = ttk.Style()
    estilo.theme_use("clam")  # Usamos el tema clam para los widgets de ttk
    
    estilo.configure("Custom.TButton", 
                     background="#37474F",  # Gris oscuro
                     foreground="white", 
                     font=("Helvetica", 10, "bold"),
                     padding=8,
                     borderwidth=0,
                     width=15)
    estilo.map("Custom.TButton",
               background=[("active", "#455A64")],
               foreground=[("active", "white")])

    estilo.configure("TFrame", background="#263238")  # Fondo oscuro
    estilo.configure("TLabel", background="#263238", font=("Helvetica", 11), foreground="#FFFFFF")
    estilo.configure("Header.TLabel", background="#263238", font=("Helvetica", 14, "bold"), foreground="#64B5F6")  # Azul claro
