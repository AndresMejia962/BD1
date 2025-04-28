import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
from mysql.connector import Error
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
import os

# Definir la función conectar_db
def conectar_db():
    try:
        return mysql.connector.connect(
            host="localhost",
            user="root",
            password="mi_contraseña123",  # Reemplaza con tu contraseña
            database="inventario_facturacion"  # Reemplaza con el nombre de tu base de datos
        )
    except Error as e:
        messagebox.showerror("Error de Conexión", f"No se pudo conectar a la base de datos: {e}")
        return None

# Configurar estilos
def configurar_estilos():
    style = ttk.Style()
    style.configure("Custom.TButton", font=("Helvetica", 10), padding=5)

configurar_estilos()

def generar_reportes(usuario_rol):
    if usuario_rol != "admin":
        messagebox.showwarning("Acceso Denegado", "Solo los administradores pueden generar reportes.")
        return

    def reporte_ventas():
        try:
            print("Iniciando generación del reporte de ventas...")
            db = conectar_db()
            if db is None:
                print("Error: No se pudo conectar a la base de datos.")
                return
            cursor = db.cursor()
            cursor.execute("""
                SELECT p.pedido_id, c.nombre, p.fecha, p.total, p.nombre_cliente_no_registrado, p.cedula_cliente_no_registrado
                FROM pedidos p
                LEFT JOIN clientes c ON p.cliente_id = c.cliente_id
            """)
            ventas = cursor.fetchall()
            db.close()
            print(f"Se encontraron {len(ventas)} ventas.")

            ventana_reporte = tk.Toplevel()
            ventana_reporte.title("Reporte de Ventas")
            ventana_reporte.geometry("800x450")
            ventana_reporte.configure(bg="#2E2E2E")

            columnas = ("ID", "Cliente", "Cédula", "Fecha", "Total")
            tabla = ttk.Treeview(ventana_reporte, columns=columnas, show="headings", height=10)

            for col in columnas:
                tabla.heading(col, text=col)
                tabla.column(col, anchor="center", width=120)

            tabla.column("Cliente", width=150)
            tabla.column("Cédula", width=120)
            tabla.column("Fecha", width=150)

            datos_exportar = []
            for venta in ventas:
                cliente = venta[1]
                cedula = None
                if venta[1]:
                    db_temp = conectar_db()
                    if db_temp is None:
                        print("Error: No se pudo conectar a la base de datos para obtener cédula.")
                        return
                    cursor_temp = db_temp.cursor()
                    cursor_temp.execute("SELECT cedula FROM clientes WHERE nombre = %s", (venta[1],))
                    cedula = cursor_temp.fetchone()
                    if cedula:
                        cedula = cedula[0]
                    else:
                        cedula = "-"
                    db_temp.close()
                elif venta[4]:
                    cliente = venta[4]
                    cedula = venta[5]
                else:
                    cliente = "No registrado"
                    cedula = "-"

                tabla.insert("", tk.END, values=(venta[0], cliente, cedula, venta[2], venta[3]))
                datos_exportar.append((venta[0], cliente, cedula, venta[2], venta[3]))

            scrollbar = ttk.Scrollbar(ventana_reporte, orient="vertical", command=tabla.yview)
            tabla.configure(yscrollcommand=scrollbar.set)

            tabla.pack(fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")
            print("Tabla de ventas creada correctamente.")

            frame_exportar = ttk.Frame(ventana_reporte)
            frame_exportar.pack(fill="x", pady=10)
            print("Frame de exportación creado.")

            def exportar_excel():
                try:
                    print("Exportando a Excel...")
                    df = pd.DataFrame(datos_exportar, columns=columnas)
                    df.to_excel("reporte_ventas.xlsx", index=False)
                    messagebox.showinfo("Éxito", "Reporte de ventas exportado a 'reporte_ventas.xlsx'")
                except Exception as e:
                    messagebox.showerror("Error", f"No se pudo exportar a Excel: {e}")
                    print(f"Error al exportar a Excel: {e}")

            def exportar_pdf():
                try:
                    print("Exportando a PDF...")
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
                    print(f"Error al exportar a PDF: {e}")

            btn_exportar_excel = ttk.Button(frame_exportar, text="Exportar a Excel", command=exportar_excel, style="Custom.TButton")
            btn_exportar_excel.pack(side="left", padx=5)
            print("Botón 'Exportar a Excel' creado.")

            btn_exportar_pdf = ttk.Button(frame_exportar, text="Exportar a PDF", command=exportar_pdf, style="Custom.TButton")
            btn_exportar_pdf.pack(side="left", padx=5)
            print("Botón 'Exportar a PDF' creado.")

            btn_cerrar = ttk.Button(ventana_reporte, text="Cerrar", command=ventana_reporte.destroy, style="Custom.TButton")
            btn_cerrar.pack(pady=10)
            print("Botón 'Cerrar' creado.")

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo generar el reporte: {e}")
            print(f"Error en reporte_ventas: {e}")

    def reporte_inventario():
        try:
            print("Iniciando generación del reporte de inventario...")
            db = conectar_db()
            if db is None:
                print("Error: No se pudo conectar a la base de datos.")
                return
            cursor = db.cursor()
            cursor.execute("""
                SELECT 
                    nombre,
                    stock,
                    precio,
                    (stock * precio) AS valor_inventario
                FROM productos
            """)
            inventario = cursor.fetchall()
            db.close()
            print(f"Se encontraron {len(inventario)} productos.")

            ventana_reporte = tk.Toplevel()
            ventana_reporte.title("Reporte de Inventario")
            ventana_reporte.geometry("600x450")
            ventana_reporte.configure(bg="#2E2E2E")

            columnas = ("Producto", "Stock", "Precio", "Valor Inventario")
            tabla = ttk.Treeview(ventana_reporte, columns=columnas, show="headings", height=10)

            for col in columnas:
                tabla.heading(col, text=col)
                tabla.column(col, anchor="center", width=120)

            tabla.column("Producto", width=200)

            datos_exportar = []
            for producto in inventario:
                tabla.insert("", tk.END, values=producto)
                datos_exportar.append(producto)

            scrollbar = ttk.Scrollbar(ventana_reporte, orient="vertical", command=tabla.yview)
            tabla.configure(yscrollcommand=scrollbar.set)

            tabla.pack(fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")
            print("Tabla de inventario creada correctamente.")

            # Sección de botones de exportación
            frame_exportar = ttk.Frame(ventana_reporte)
            frame_exportar.pack(fill="x", pady=10)
            print("Frame de exportación creado.")  # Depuración

            def exportar_excel():
                try:
                    print("Exportando a Excel...")
                    df = pd.DataFrame(datos_exportar, columns=columnas)
                    df.to_excel("reporte_inventario.xlsx", index=False)
                    messagebox.showinfo("Éxito", "Reporte de inventario exportado a 'reporte_inventario.xlsx'")
                except Exception as e:
                    messagebox.showerror("Error", f"No se pudo exportar a Excel: {e}")
                    print(f"Error al exportar a Excel: {e}")

            def exportar_pdf():
                try:
                    print("Exportando a PDF...")
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
                    print(f"Error al exportar a PDF: {e}")

            btn_exportar_excel = ttk.Button(frame_exportar, text="Exportar a Excel", command=exportar_excel, style="Custom.TButton")
            btn_exportar_excel.pack(side="left", padx=5)
            print("Botón 'Exportar a Excel' creado.")  # Depuración

            btn_exportar_pdf = ttk.Button(frame_exportar, text="Exportar a PDF", command=exportar_pdf, style="Custom.TButton")
            btn_exportar_pdf.pack(side="left", padx=5)
            print("Botón 'Exportar a PDF' creado.")  # Depuración

            btn_cerrar = ttk.Button(ventana_reporte, text="Cerrar", command=ventana_reporte.destroy, style="Custom.TButton")
            btn_cerrar.pack(pady=10)
            print("Botón 'Cerrar' creado.")

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo generar el reporte: {e}")
            print(f"Error en reporte_inventario: {e}")

    def reporte_pagos():
        try:
            print("Iniciando generación del reporte de pagos...")
            db = conectar_db()
            if db is None:
                print("Error: No se pudo conectar a la base de datos.")
                return
            cursor = db.cursor()
            cursor.execute("""
                SELECT p.pago_id, c.nombre, p.monto, p.fecha_pago, p.metodo_pago, pd.nombre_cliente_no_registrado, pd.cedula_cliente_no_registrado
                FROM pagos p
                JOIN pedidos pd ON p.pedido_id = pd.pedido_id
                LEFT JOIN clientes c ON pd.cliente_id = c.cliente_id
            """)
            pagos = cursor.fetchall()
            db.close()
            print(f"Se encontraron {len(pagos)} pagos.")

            ventana_reporte = tk.Toplevel()
            ventana_reporte.title("Reporte de Pagos")
            ventana_reporte.geometry("800x450")
            ventana_reporte.configure(bg="#2E2E2E")

            columnas = ("ID", "Cliente", "Cédula", "Monto", "Fecha", "Método de Pago")
            tabla = ttk.Treeview(ventana_reporte, columns=columnas, show="headings", height=10)

            for col in columnas:
                tabla.heading(col, text=col)
                tabla.column(col, anchor="center", width=120)

            tabla.column("Cliente", width=150)
            tabla.column("Cédula", width=120)
            tabla.column("Fecha", width=150)

            datos_exportar = []
            for pago in pagos:
                cliente = pago[1]
                cedula = None
                if pago[1]:
                    db_temp = conectar_db()
                    if db_temp is None:
                        print("Error: No se pudo conectar a la base de datos para obtener cédula.")
                        return
                    cursor_temp = db_temp.cursor()
                    cursor_temp.execute("SELECT cedula FROM clientes WHERE nombre = %s", (pago[1],))
                    cedula = cursor_temp.fetchone()
                    if cedula:
                        cedula = cedula[0]
                    else:
                        cedula = "-"
                    db_temp.close()
                elif pago[5]:
                    cliente = pago[5]
                    cedula = pago[6]
                else:
                    cliente = "No registrado"
                    cedula = "-"

                tabla.insert("", tk.END, values=(pago[0], cliente, cedula, pago[2], pago[3], pago[4]))
                datos_exportar.append((pago[0], cliente, cedula, pago[2], pago[3], pago[4]))

            scrollbar = ttk.Scrollbar(ventana_reporte, orient="vertical", command=tabla.yview)
            tabla.configure(yscrollcommand=scrollbar.set)

            tabla.pack(fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")
            print("Tabla de pagos creada correctamente.")

            frame_exportar = ttk.Frame(ventana_reporte)
            frame_exportar.pack(fill="x", pady=10)
            print("Frame de exportación creado.")

            def exportar_excel():
                try:
                    print("Exportando a Excel...")
                    df = pd.DataFrame(datos_exportar, columns=columnas)
                    df.to_excel("reporte_pagos.xlsx", index=False)
                    messagebox.showinfo("Éxito", "Reporte de pagos exportado a 'reporte_pagos.xlsx'")
                except Exception as e:
                    messagebox.showerror("Error", f"No se pudo exportar a Excel: {e}")
                    print(f"Error al exportar a Excel: {e}")

            def exportar_pdf():
                try:
                    print("Exportando a PDF...")
                    pdf_file = "reporte_pagos.pdf"
                    doc = SimpleDocTemplate(pdf_file, pagesize=letter)
                    elements = []

                    styles = getSampleStyleSheet()
                    elements.append(Paragraph("Reporte de Pagos", styles['Title']))

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
                    messagebox.showinfo("Éxito", f"Reporte de pagos exportado a '{pdf_file}'")
                except Exception as e:
                    messagebox.showerror("Error", f"No se pudo exportar a PDF: {e}")
                    print(f"Error al exportar a PDF: {e}")

            btn_exportar_excel = ttk.Button(frame_exportar, text="Exportar a Excel", command=exportar_excel, style="Custom.TButton")
            btn_exportar_excel.pack(side="left", padx=5)
            print("Botón 'Exportar a Excel' creado.")

            btn_exportar_pdf = ttk.Button(frame_exportar, text="Exportar a PDF", command=exportar_pdf, style="Custom.TButton")
            btn_exportar_pdf.pack(side="left", padx=5)
            print("Botón 'Exportar a PDF' creado.")

            btn_cerrar = ttk.Button(ventana_reporte, text="Cerrar", command=ventana_reporte.destroy, style="Custom.TButton")
            btn_cerrar.pack(pady=10)
            print("Botón 'Cerrar' creado.")

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo generar el reporte: {e}")
            print(f"Error en reporte_pagos: {e}")

    ventana_reportes = tk.Toplevel()
    ventana_reportes.title("Generar Reportes")
    ventana_reportes.geometry("300x200")
    ventana_reportes.configure(bg="#2E2E2E")
    ventana_reportes.resizable(False, False)

    frame = ttk.Frame(ventana_reportes)
    frame.pack(padx=10, pady=10, fill="both", expand=True)

    btn_ventas = ttk.Button(frame, text="Reporte de Ventas", command=reporte_ventas, style="Custom.TButton")
    btn_ventas.pack(pady=10)

    btn_inventario = ttk.Button(frame, text="Reporte de Inventario", command=reporte_inventario, style="Custom.TButton")
    btn_inventario.pack(pady=10)

    btn_pagos = ttk.Button(frame, text="Reporte de Pagos", command=reporte_pagos, style="Custom.TButton")
    btn_pagos.pack(pady=10)

    btn_cerrar = ttk.Button(frame, text="Cerrar", command=ventana_reportes.destroy, style="Custom.TButton")
    btn_cerrar.pack(pady=10)