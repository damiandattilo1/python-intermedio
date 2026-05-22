from tkinter import *
from tkinter import ttk
import controlador


def crear_interfaz():

    root = Tk()
    root.title("Gestión de Materias")

    frm = ttk.Frame(root, padding=10)
    frm.grid()

    widgets = {}

    # ---------------------
    # ETIQUETAS Y ENTRADAS
    # ---------------------

    ttk.Label(frm, text="Nivel").grid(row=0, column=0, padx=5, pady=5)

    widgets["nivel"] = ttk.Combobox(frm, values=["1", "2", "3", "4", "5"])
    widgets["nivel"].grid(row=0, column=1, padx=5, pady=5)

    ttk.Label(frm, text="Nombre").grid(row=1, column=0, padx=5, pady=5)

    widgets["nombre"] = ttk.Entry(frm)
    widgets["nombre"].grid(row=1, column=1, padx=5, pady=5)

    ttk.Label(frm, text="Cargo Docente").grid(row=2, column=0, padx=5, pady=5)

    widgets["docente"] = ttk.Entry(frm)
    widgets["docente"].grid(row=2, column=1, padx=5, pady=5)

    ttk.Label(frm, text="Cantidad Horas").grid(row=3, column=0, padx=5, pady=5)

    widgets["cantidadHoras"] = ttk.Entry(frm)
    widgets["cantidadHoras"].grid(row=3, column=1, padx=5, pady=5)

    # ---------------------
    # TREEVIEW
    # ---------------------

    tree = ttk.Treeview(
        frm,
        columns=("id", "nivel", "nombre", "docente", "cantidadHoras"),
        show="headings"
    )

    for col in ("id", "nivel", "nombre", "docente", "cantidadHoras"):
        tree.heading(col, text=col)

    tree.grid(row=5, column=0, columnspan=4, pady=10)

    # ---------------------
    # FUNCIONES UI
    # ---------------------

    def actualizar_tabla():
        for fila in tree.get_children():
            tree.delete(fila)

        for fila in controlador.Materia.listar():
            tree.insert("", "end", values=fila)

    def agregar():
        datos = (
            widgets["nivel"].get(),
            widgets["nombre"].get(),
            widgets["docente"].get(),
            widgets["cantidadHoras"].get(),
        )

        controlador.Materia.agregar(datos)
        actualizar_tabla()

    def eliminar():
        seleccion = tree.selection()

        if not seleccion:
            return

        item = tree.item(seleccion)
        mi_id = item["values"][0]

        controlador.eliminar(mi_id)
        actualizar_tabla()

    def modificar():
        seleccion = tree.selection()

        if not seleccion:
            return

        item = tree.item(seleccion)
        mi_id = item["values"][0]

        nuevo = widgets["docente"].get()

        controlador.modificar_docente(mi_id, nuevo)
        actualizar_tabla()

    # ---------------------
    # BOTONES
    # ---------------------

    ttk.Button(frm, text="Agregar", command=agregar).grid(row=4, column=0, padx=5)
    ttk.Button(frm, text="Eliminar", command=eliminar).grid(row=4, column=1, padx=5)
    ttk.Button(frm, text="Modificar", command=modificar).grid(row=4, column=2, padx=5)
    ttk.Button(frm, text="Listar", command=actualizar_tabla).grid(row=4, column=3, padx=5)

    root.mainloop()