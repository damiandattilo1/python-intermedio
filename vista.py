import tkinter as tk
from tkinter import ttk, messagebox
import controlador


def crear_interfaz():

    root = tk.Tk()
    root.title("Gestion de Materias")
    root.minsize(600, 450)

    # Centrar ventana
    root.update_idletasks()
    w, h = 620, 470
    x = (root.winfo_screenwidth() // 2) - (w // 2)
    y = (root.winfo_screenheight() // 2) - (h // 2)
    root.geometry(f"{w}x{h}+{x}+{y}")

    main = ttk.Frame(root, padding=10)
    main.pack(fill="both", expand=True)

    # ---------------------
    # FORMULARIO
    # ---------------------

    form_frame = ttk.LabelFrame(main, text=" Nueva Materia ", padding=10)
    form_frame.pack(fill="x", pady=(0, 10))

    campos = [
        ("Nivel:", "nivel", ttk.Combobox(form_frame, values=["1", "2", "3", "4", "5"], width=5, state="readonly")),
        ("Nombre:", "nombre", ttk.Entry(form_frame, width=30)),
        ("Docente:", "docente", ttk.Entry(form_frame, width=30)),
        ("Horas:", "horas", ttk.Entry(form_frame, width=8)),
    ]

    widgets = {}
    for i, (label, key, widget) in enumerate(campos):
        ttk.Label(form_frame, text=label).grid(row=0, column=i * 2, padx=(8 if i > 0 else 0, 4), pady=2, sticky="e")
        widget.grid(row=0, column=i * 2 + 1, padx=(0, 8), pady=2, sticky="w")
        widgets[key] = widget

    widgets["nivel"].current(0)

    # ---------------------
    # BOTONES
    # ---------------------

    btn_frame = ttk.Frame(main)
    btn_frame.pack(fill="x", pady=(0, 10))

    btn_agregar = ttk.Button(btn_frame, text="Agregar", command=lambda: None)
    btn_eliminar = ttk.Button(btn_frame, text="Eliminar", command=lambda: None)
    btn_modificar = ttk.Button(btn_frame, text="Modificar", command=lambda: None)

    btn_agregar.pack(side="left", padx=(0, 5))
    btn_eliminar.pack(side="left", padx=5)
    btn_modificar.pack(side="left", padx=5)

    # ---------------------
    # TREEVIEW
    # ---------------------

    tree_frame = ttk.Frame(main)
    tree_frame.pack(fill="both", expand=True)

    columnas = ("id", "nivel", "nombre", "docente", "horas")
    encabezados = {"id": "ID", "nivel": "Nivel", "nombre": "Nombre", "docente": "Docente", "horas": "Horas"}

    tree = ttk.Treeview(tree_frame, columns=columnas, show="headings", selectmode="browse")

    tree.column("id", width=40, anchor="center")
    tree.column("nivel", width=50, anchor="center")
    tree.column("nombre", width=180)
    tree.column("docente", width=180)
    tree.column("horas", width=60, anchor="center")

    for col in columnas:
        tree.heading(col, text=encabezados[col])

    scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)

    tree.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    # ---------------------
    # FUNCIONES UI
    # ---------------------

    def limpiar_formulario():
        widgets["nombre"].delete(0, "end")
        widgets["docente"].delete(0, "end")
        widgets["horas"].delete(0, "end")
        widgets["nivel"].current(0)

    def cargar_seleccion(event=None):
        seleccion = tree.selection()
        if not seleccion:
            return
        valores = tree.item(seleccion[0])["values"]
        widgets["nivel"].set(valores[1])
        widgets["nombre"].delete(0, "end")
        widgets["nombre"].insert(0, valores[2])
        widgets["docente"].delete(0, "end")
        widgets["docente"].insert(0, valores[3])
        widgets["horas"].delete(0, "end")
        widgets["horas"].insert(0, valores[4])

    def actualizar_tabla():
        for fila in tree.get_children():
            tree.delete(fila)
        for fila in controlador.Materia.listar():
            tree.insert("", "end", values=fila)

    def agregar():
        nivel = widgets["nivel"].get()
        nombre = widgets["nombre"].get().strip()
        docente = widgets["docente"].get().strip()
        horas = widgets["horas"].get().strip()

        if not nombre or not docente or not horas:
            messagebox.showwarning("Campos requeridos", "Complete todos los campos antes de agregar.")
            return

        datos = (nivel, nombre, docente, horas)
        controlador.Materia.agregar(datos)
        limpiar_formulario()
        actualizar_tabla()

    def eliminar():
        seleccion = tree.selection()
        if not seleccion:
            messagebox.showinfo("Seleccion requerida", "Seleccione una materia para eliminar.")
            return

        valores = tree.item(seleccion[0])["values"]
        if messagebox.askyesno("Confirmar", f"Eliminar materia '{valores[2]}'?"):
            controlador.Materia.eliminar(int(valores[0]))
            actualizar_tabla()

    def modificar():
        seleccion = tree.selection()
        if not seleccion:
            messagebox.showinfo("Seleccion requerida", "Seleccione una materia para modificar.")
            return

        valores = tree.item(seleccion[0])["values"]
        mi_id = int(valores[0])
        nuevo = widgets["docente"].get().strip()

        if not nuevo:
            messagebox.showwarning("Campo requerido", "Ingrese el nuevo nombre del docente.")
            return

        controlador.Materia.modificar_docente(mi_id, nuevo)
        actualizar_tabla()

    # Asignar comandos reales
    btn_agregar.config(command=agregar)
    btn_eliminar.config(command=eliminar)
    btn_modificar.config(command=modificar)

    tree.bind("<<TreeviewSelect>>", cargar_seleccion)

    # Cargar datos al iniciar
    actualizar_tabla()

    root.mainloop()
