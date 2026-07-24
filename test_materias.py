import os
import sqlite3
import tempfile
import unittest

import modelo
import controlador


class TestModelo(unittest.TestCase):

    def setUp(self):
        self.con = sqlite3.connect(":memory:")
        modelo.crear_tabla(self.con)

    def tearDown(self):
        self.con.close()

    def test_insertar_y_obtener(self):
        datos = ("1", "Mate", "Juan Perez", "4")
        modelo.insertar(self.con, datos)
        filas = modelo.obtener_todos(self.con)
        self.assertEqual(len(filas), 1)
        self.assertEqual(filas[0][2], "Mate")
        self.assertEqual(filas[0][3], "Juan Perez")

    def test_borrar(self):
        modelo.insertar(self.con, ("1", "Mate", "Juan", "4"))
        filas = modelo.obtener_todos(self.con)
        mi_id = filas[0][0]
        modelo.borrar(self.con, mi_id)
        self.assertEqual(modelo.obtener_todos(self.con), [])

    def test_actualizar_materia(self):
        modelo.insertar(self.con, ("1", "Mate", "Juan", "4"))
        filas = modelo.obtener_todos(self.con)
        mi_id = filas[0][0]
        modelo.actualizar_materia(self.con, "Algebra", "Maria Lopez", mi_id)
        filas = modelo.obtener_todos(self.con)
        self.assertEqual(filas[0][2], "Algebra")
        self.assertEqual(filas[0][3], "Maria Lopez")

    def test_crear_tabla_idempotente(self):
        modelo.crear_tabla(self.con)
        modelo.crear_tabla(self.con)
        modelo.insertar(self.con, ("2", "Fis", "Ana", "3"))
        filas = modelo.obtener_todos(self.con)
        self.assertEqual(len(filas), 1)


class TestControlador(unittest.TestCase):

    def setUp(self):
        self._tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self._tmp.close()
        self._db_path = self._tmp.name
        self._orig_crear_base = modelo.crear_base
        modelo.crear_base = lambda: sqlite3.connect(self._db_path)
        con = modelo.crear_base()
        modelo.crear_tabla(con)
        con.close()

    def tearDown(self):
        modelo.crear_base = self._orig_crear_base
        os.unlink(self._db_path)

    def test_validar_profesor_valido(self):
        self.assertTrue(controlador.Materia.validar_profesor("Juan Perez"))
        self.assertTrue(controlador.Materia.validar_profesor("Maria"))

    def test_validar_profesor_invalido(self):
        self.assertFalse(controlador.Materia.validar_profesor(""))
        self.assertFalse(controlador.Materia.validar_profesor("Juan123"))
        self.assertFalse(controlador.Materia.validar_profesor(" Juan"))

    def test_agregar_profesor_valido(self):
        datos = ("1", "Mate", "Juan Perez", "4")
        controlador.Materia.agregar(datos)
        filas = controlador.Materia.listar()
        self.assertEqual(len(filas), 1)
        self.assertEqual(filas[0][3], "Juan Perez")

    def test_agregar_profesor_invalido_no_inserta(self):
        datos = ("1", "Mate", "Juan123", "4")
        controlador.Materia.agregar(datos)
        self.assertEqual(controlador.Materia.listar(), [])

    def test_listar_vacio(self):
        self.assertEqual(controlador.Materia.listar(), [])

    def test_eliminar(self):
        controlador.Materia.agregar(("1", "Mate", "Juan Perez", "4"))
        filas = controlador.Materia.listar()
        mi_id = filas[0][0]
        controlador.Materia.eliminar(mi_id)
        self.assertEqual(controlador.Materia.listar(), [])

    def test_modificar_materia(self):
        controlador.Materia.agregar(("1", "Mate", "Juan Perez", "4"))
        filas = controlador.Materia.listar()
        mi_id = filas[0][0]
        controlador.Materia.modificar(mi_id, "Algebra", "Maria Lopez")
        filas = controlador.Materia.listar()
        self.assertEqual(filas[0][2], "Algebra")
        self.assertEqual(filas[0][3], "Maria Lopez")


class TestRutaBaseDatos(unittest.TestCase):

    def test_ruta_es_relativa_al_archivo(self):
        ruta = os.path.join(os.path.dirname(os.path.abspath(modelo.__file__)), "materias.db")
        self.assertTrue(os.path.dirname(ruta).endswith("python-intermedio"))


if __name__ == "__main__":
    unittest.main()
