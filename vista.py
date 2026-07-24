import tkinter as tk
from tkinter import ttk, messagebox
from modelo import Materia
from controlador import MateriaControlador
from observador import LogObserver


def crear_interfaz():

    ctrl = MateriaControlador()
    ctrl.agregar_observador(LogObserver())

    root = tk.Tk()
    root.title("Gestion de Materias")
    root.minsize(750, 480)

    # Centrar ventana
    root.update_idletasks()
    w, h = 780, 500
    x = (root.winfo_screenwidth() // 2) - (w // 2)
    y = (root.winfo_screenheight() // 2) - (h // 2)
    root.geometry(f"{w}x{h}+{x}+{y}")

    estilo = ttk.Style()
    estilo.configure("Treeview", rowheight=24)
    estilo.map("Treeview", background=[("selected", "#0078d4")])

    main = ttk.Frame(root, padding=10)
    main.pack(fill="both", expand=True)

    # ---------------------
    # FORMULARIO
    # ---------------------

    form_frame = ttk.LabelFrame(main, text=" Datos de la Materia ", padding=(12, 6))
    form_frame.pack(fill="x", pady=(0, 8))

    campos = [
        ("Nivel:", "nivel", ttk.Combobox(form_frame, values=["1", "2", "3", "4", "5"], width=5, state="readonly")),
        ("Nombre:", "nombre", ttk.Entry(form_frame, width=28)),
        ("Docente:", "docente", ttk.Entry(form_frame, width=28)),
        ("Horas:", "horas", ttk.Entry(form_frame, width=6)),
    ]

    widgets = {}
    for i, (label, key, widget) in enumerate(campos):
        ttk.Label(form_frame, text=label).grid(row=0, column=i * 2, padx=(10 if i > 0 else 0, 4), pady=4, sticky="e")
        widget.grid(row=0, column=i * 2 + 1, padx=(0, 10), pady=4, sticky="w")
        widgets[key] = widget

    widgets["nivel"].current(0)

    # ---------------------
    # BOTONES
    # ---------------------

    btn_frame = ttk.Frame(main)
    btn_frame.pack(fill="x", pady=(0, 8))

    btn_agregar = ttk.Button(btn_frame, text="Agregar")
    btn_modificar = ttk.Button(btn_frame, text="Guardar cambios")
    btn_eliminar = ttk.Button(btn_frame, text="Eliminar")

    btn_agregar.pack(side="left", padx=(0, 5))
    btn_modificar.pack(side="left", padx=5)
    btn_eliminar.pack(side="left", padx=5)

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
    tree.column("nombre", width=220)
    tree.column("docente", width=220)
    tree.column("horas", width=60, anchor="center")

    for col in columnas:
        tree.heading(col, text=encabezados[col])

    scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)

    tree.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    tree.tag_configure("par", background="#f0f0f0")
    tree.tag_configure("impar", background="#ffffff")

    # ---------------------
    # BARRA DE ESTADO
    # ---------------------

    status_var = tk.StringVar(value="Materias: 0")
    status_bar = ttk.Label(root, textvariable=status_var, relief="sunken", anchor="w", padding=(6, 2))
    status_bar.pack(side="bottom", fill="x")

    # ---------------------
    # FUNCIONES UI
    # ---------------------

    def limpiar_formulario():
        widgets["nombre"].delete(0, "end")
        widgets["docente"].delete(0, "end")
        widgets["horas"].delete(0, "end")
        widgets["nivel"].current(0)
        widgets["nombre"].focus_set()

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

        materias = ctrl.listar()
        for i, m in enumerate(materias):
            tag = "par" if i % 2 == 0 else "impar"
            tree.insert("", "end", values=(m.id, m.nivel, m.nombre, m.docente, m.horas), tags=(tag,))

        status_var.set(f"Materias: {len(materias)}")

    def agregar():
        nivel = widgets["nivel"].get()
        nombre = widgets["nombre"].get().strip()
        docente = widgets["docente"].get().strip()
        horas = widgets["horas"].get().strip()

        if not nombre or not docente or not horas:
            messagebox.showwarning("Campos requeridos", "Complete todos los campos antes de agregar.")
            return

        if not horas.isdigit() or int(horas) <= 0:
            messagebox.showwarning("Horas invalidas", "Las horas deben ser un numero entero mayor a 0.")
            return

        materia = Materia(nivel=nivel, nombre=nombre, docente=docente, horas=int(horas))
        ok, msg = ctrl.agregar(materia)
        if not ok:
            messagebox.showwarning("Error de validacion", msg)
            return

        limpiar_formulario()
        actualizar_tabla()

    def eliminar():
        seleccion = tree.selection()
        if not seleccion:
            messagebox.showinfo("Seleccion requerida", "Seleccione una materia para eliminar.")
            return

        valores = tree.item(seleccion[0])["values"]
        if messagebox.askyesno("Confirmar", f"Eliminar materia '{valores[2]}'?"):
            ctrl.eliminar(int(valores[0]))
            limpiar_formulario()
            actualizar_tabla()

    def modificar():
        seleccion = tree.selection()
        if not seleccion:
            messagebox.showinfo("Seleccion requerida", "Seleccione una materia para modificar.")
            return

        valores = tree.item(seleccion[0])["values"]
        nivel = widgets["nivel"].get()
        nombre = widgets["nombre"].get().strip()
        docente = widgets["docente"].get().strip()
        horas = widgets["horas"].get().strip()

        if not nombre or not docente or not horas:
            messagebox.showwarning("Campos requeridos", "Complete todos los campos.")
            return

        if not horas.isdigit() or int(horas) <= 0:
            messagebox.showwarning("Horas invalidas", "Las horas deben ser un numero entero mayor a 0.")
            return

        materia = Materia(id=int(valores[0]), nivel=nivel, nombre=nombre, docente=docente, horas=int(horas))
        ctrl.modificar(materia)
        actualizar_tabla()

    # Asignar comandos
    btn_agregar.config(command=agregar)
    btn_modificar.config(command=modificar)
    btn_eliminar.config(command=eliminar)

    tree.bind("<<TreeviewSelect>>", cargar_seleccion)

    root.bind("<Return>", lambda e: agregar())
    root.bind("<Delete>", lambda e: eliminar())

    widgets["nombre"].focus_set()
    actualizar_tabla()

    root.mainloop()
