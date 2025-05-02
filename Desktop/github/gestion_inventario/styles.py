from tkinter import ttk

def aplicar_estilo():
    estilo = ttk.Style()
    estilo.theme_use("clam")

    # Configuración de estilos responsivos
    estilo.configure("TFrame", background="#263238")
    estilo.configure("Sidebar.TFrame", background="#1C313A")
    estilo.configure("Summary.TFrame", background="#263238")
    estilo.configure("TLabelFrame", background="#263238")
    estilo.configure("TLabelFrame.Label", 
                    background="#263238", 
                    foreground="#E0E0E0", 
                    font=("Helvetica", 12, "bold"))

    # Estilos responsivos para botones
    estilo.configure("Custom.TButton", 
                    background="#37474F",
                    foreground="white", 
                    font=("Helvetica", 10, "bold"),
                    padding=8,
                    borderwidth=0)
    
    # Estilos responsivos para etiquetas
    estilo.configure("TLabel", 
                    background="#263238", 
                    font=("Helvetica", 11), 
                    foreground="#E0E0E0",
                    wraplength=300)  # Permite que el texto se ajuste

    # Estilos responsivos para el encabezado
    estilo.configure("Header.TLabel", 
                    background="#263238", 
                    font=("Helvetica", 16, "bold"), 
                    foreground="#64B5F6",
                    wraplength=400)  # Permite que el texto se ajuste

    # Estilos responsivos para las métricas
    estilo.configure("Metric.TFrame",
                    background="#37474F",
                    relief="raised",
                    borderwidth=1)

    estilo.configure("Metric.TLabel",
                    background="#37474F",
                    font=("Helvetica", 11),
                    foreground="#E0E0E0",
                    padding=10,
                    wraplength=200)  # Permite que el texto se ajuste

    # Estilos responsivos para el Treeview
    estilo.configure("Treeview", 
                    background="#37474F",
                    foreground="white", 
                    rowheight=25,
                    fieldbackground="#263238")
    
    estilo.configure("Treeview.Heading", 
                    background="#455A64",
                    foreground="white", 
                    font=("Helvetica", 10, "bold"))

    # Configuración de estilos para diferentes tamaños de pantalla
    def configurar_estilos_responsivos(event=None):
        width = event.width if event else 800
        if width < 600:
            # Estilos para pantallas pequeñas
            estilo.configure("TLabel", font=("Helvetica", 9))
            estilo.configure("Header.TLabel", font=("Helvetica", 14, "bold"))
            estilo.configure("Custom.TButton", font=("Helvetica", 9, "bold"))
        elif width < 1024:
            # Estilos para pantallas medianas
            estilo.configure("TLabel", font=("Helvetica", 10))
            estilo.configure("Header.TLabel", font=("Helvetica", 15, "bold"))
            estilo.configure("Custom.TButton", font=("Helvetica", 10, "bold"))
        else:
            # Estilos para pantallas grandes
            estilo.configure("TLabel", font=("Helvetica", 11))
            estilo.configure("Header.TLabel", font=("Helvetica", 16, "bold"))
            estilo.configure("Custom.TButton", font=("Helvetica", 11, "bold"))

    return configurar_estilos_responsivos

def aplicar_estilo_login():
    estilo = ttk.Style()
    estilo.theme_use("clam")
    
    # Estilos responsivos para el login
    estilo.configure("Custom.TButton", 
                    background="#37474F",
                    foreground="white", 
                    font=("Helvetica", 10, "bold"),
                    padding=8,
                    borderwidth=0)

    estilo.configure("TFrame", background="#263238")
    estilo.configure("TLabel", 
                    background="#263238", 
                    font=("Helvetica", 11), 
                    foreground="#FFFFFF",
                    wraplength=300)  # Permite que el texto se ajuste
    
    estilo.configure("Header.TLabel", 
                    background="#263238", 
                    font=("Helvetica", 14, "bold"), 
                    foreground="#64B5F6",
                    wraplength=350)  # Permite que el texto se ajuste
