import tkinter as tk
from tkinter import messagebox

class ShortcutManager:
    def __init__(self, ventana_principal):
        self.ventana_principal = ventana_principal
        self.configurar_atajos()

    def configurar_atajos(self):
        # Atajos globales
        self.ventana_principal.bind('<Control-q>', lambda e: self.cerrar_sesion())
        self.ventana_principal.bind('<F1>', lambda e: self.mostrar_ayuda())
        self.ventana_principal.bind('<F5>', lambda e: self.actualizar_resumen())
        
        # Atajos de navegación
        self.ventana_principal.bind('<Control-p>', lambda e: self.consultar_productos())
        self.ventana_principal.bind('<Control-n>', lambda e: self.agregar_producto())
        self.ventana_principal.bind('<Control-v>', lambda e: self.registrar_venta())
        self.ventana_principal.bind('<Control-r>', lambda e: self.generar_reportes())
        
        # Atajos de gestión (Control + Shift)
        self.ventana_principal.bind('<Control-P>', lambda e: self.gestionar_proveedores())  # Control + Shift + P
        self.ventana_principal.bind('<Control-C>', lambda e: self.gestionar_clientes())     # Control + Shift + C
        self.ventana_principal.bind('<Control-E>', lambda e: self.gestionar_empleados())    # Control + Shift + E

    def cerrar_sesion(self):
        if messagebox.askyesno("Confirmar", "¿Estás seguro de que deseas cerrar sesión?"):
            self.ventana_principal.quit()

    def mostrar_ayuda(self):
        ayuda_texto = """
        Atajos de Teclado Disponibles:
        
        Ctrl + Q: Cerrar sesión
        F1: Mostrar ayuda
        F5: Actualizar resumen
        
        Ctrl + p: Consultar productos
        Ctrl + n: Agregar producto
        Ctrl + v: Registrar venta
        Ctrl + r: Generar reportes
        
        Ctrl + Shift + P: Gestionar proveedores
        Ctrl + Shift + C: Gestionar clientes
        Ctrl + Shift + E: Gestionar empleados
        """
        messagebox.showinfo("Ayuda - Atajos de Teclado", ayuda_texto)

    def actualizar_resumen(self):
        # Esta función se implementará en ui.py
        pass

    def consultar_productos(self):
        # Esta función se implementará en ui.py
        pass

    def agregar_producto(self):
        # Esta función se implementará en ui.py
        pass

    def registrar_venta(self):
        # Esta función se implementará en ui.py
        pass

    def generar_reportes(self):
        # Esta función se implementará en ui.py
        pass

    def gestionar_proveedores(self):
        # Esta función se implementará en ui.py
        pass

    def gestionar_clientes(self):
        # Esta función se implementará en ui.py
        pass

    def gestionar_empleados(self):
        # Esta función se implementará en ui.py
        pass 