import io
import os
import sys
import tempfile
import unittest

from modelo import Materia, MateriaDB
from controlador import MateriaControlador
from decoradores import log_agregar, log_eliminar, log_modificar, log_registro
from observador import Subject, Observer, LogObserver, HistorialObserver


# ============================
# 1) POO
# ============================

class TestMateria(unittest.TestCase):

    def test_creacion_con_defaults(self):
        m = Materia()
        self.assertIsNone(m.id)
        self.assertEqual(m.nivel, "1")
        self.assertEqual(m.nombre, "")
        self.assertEqual(m.docente, "")
        self.assertEqual(m.horas, "4")

    def test_creacion_con_valores(self):
        m = Materia(id=1, nivel="3", nombre="Algebra", docente="Juan Perez", horas="6")
        self.assertEqual(m.id, 1)
        self.assertEqual(m.nivel, "3")
        self.assertEqual(m.nombre, "Algebra")
        self.assertEqual(m.docente, "Juan Perez")
        self.assertEqual(m.horas, "6")

    def test_equality(self):
        a = Materia(nivel="1", nombre="Mate", docente="Juan", horas="4")
        b = Materia(nivel="1", nombre="Mate", docente="Juan", horas="4")
        c = Materia(nivel="2", nombre="Fisica", docente="Ana", horas="3")
        self.assertEqual(a, b)
        self.assertNotEqual(a, c)

    def test_a_tupla(self):
        m = Materia(nivel="2", nombre="Fisica", docente="Ana", horas="3")
        self.assertEqual(m.a_tupla(), ("2", "Fisica", "Ana", "3"))

    def test_desde_fila(self):
        fila = (5, "1", "Mate", "Juan", "4")
        m = Materia.desde_fila(fila)
        self.assertEqual(m.id, 5)
        self.assertEqual(m.nombre, "Mate")

    def test_repr(self):
        m = Materia(id=1, nivel="1", nombre="Mate", docente="Juan", horas="4")
        self.assertIn("Mate", repr(m))


class TestMateriaDB(unittest.TestCase):

    def setUp(self):
        self._tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self._tmp.close()
        self.db = MateriaDB(self._tmp.name)
        self.db.crear_tabla()

    def tearDown(self):
        os.unlink(self._tmp.name)

    def test_insertar_y_obtener(self):
        m = Materia(nivel="1", nombre="Mate", docente="Juan", horas="4")
        self.db.insertar(m)
        materias = self.db.obtener_todos()
        self.assertEqual(len(materias), 1)
        self.assertEqual(materias[0].nombre, "Mate")

    def test_borrar(self):
        m = Materia(nivel="1", nombre="Mate", docente="Juan", horas="4")
        self.db.insertar(m)
        materias = self.db.obtener_todos()
        self.db.borrar(materias[0].id)
        self.assertEqual(self.db.obtener_todos(), [])

    def test_actualizar(self):
        m = Materia(nivel="1", nombre="Mate", docente="Juan", horas="4")
        self.db.insertar(m)
        materias = self.db.obtener_todos()
        materias[0].nombre = "Algebra"
        materias[0].docente = "Maria"
        self.db.actualizar(materias[0])
        result = self.db.obtener_todos()
        self.assertEqual(result[0].nombre, "Algebra")
        self.assertEqual(result[0].docente, "Maria")

    def test_obtener_por_id(self):
        m = Materia(nivel="1", nombre="Mate", docente="Juan", horas="4")
        self.db.insertar(m)
        materias = self.db.obtener_todos()
        result = self.db.obtener_por_id(materias[0].id)
        self.assertIsNotNone(result)
        self.assertEqual(result.nombre, "Mate")

    def test_obtener_por_id_inexistente(self):
        result = self.db.obtener_por_id(999)
        self.assertIsNone(result)

    def test_crear_tabla_idempotente(self):
        self.db.crear_tabla()
        m = Materia(nivel="1", nombre="Mate", docente="Juan", horas="4")
        self.db.insertar(m)
        self.assertEqual(len(self.db.obtener_todos()), 1)


# ============================
# 3) Decoradores
# ============================

class TestDecoradores(unittest.TestCase):

    def setUp(self):
        self._tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self._tmp.close()
        self.ctrl = MateriaControlador()
        self.ctrl._db = MateriaDB(self._tmp.name)
        self.ctrl._db.crear_tabla()

    def tearDown(self):
        os.unlink(self._tmp.name)

    def test_log_agregar_imprime(self):
        captured = io.StringIO()
        sys.stdout = captured
        m = Materia(nivel="1", nombre="Mate", docente="Juan Perez", horas="4")
        self.ctrl.agregar(m)
        sys.stdout = sys.__stdout__
        salida = captured.getvalue()
        self.assertIn("INGRESO", salida)
        self.assertIn("Mate", salida)

    def test_log_eliminar_imprime(self):
        m = Materia(nivel="1", nombre="Mate", docente="Juan Perez", horas="4")
        self.ctrl.agregar(m)
        materias = self.ctrl.listar()
        captured = io.StringIO()
        sys.stdout = captured
        self.ctrl.eliminar(materias[0].id)
        sys.stdout = sys.__stdout__
        salida = captured.getvalue()
        self.assertIn("ELIMINACION", salida)

    def test_log_modificar_imprime(self):
        m = Materia(nivel="1", nombre="Mate", docente="Juan Perez", horas="4")
        self.ctrl.agregar(m)
        materias = self.ctrl.listar()
        materias[0].nombre = "Algebra"
        captured = io.StringIO()
        sys.stdout = captured
        self.ctrl.modificar(materias[0])
        sys.stdout = sys.__stdout__
        salida = captured.getvalue()
        self.assertIn("ACTUALIZACION", salida)
        self.assertIn("Algebra", salida)

    def test_decorador_log_registro(self):
        @log_registro("TEST ACCION")
        def mi_funcion():
            return 42

        captured = io.StringIO()
        sys.stdout = captured
        result = mi_funcion()
        sys.stdout = sys.__stdout__
        self.assertEqual(result, 42)
        self.assertIn("TEST ACCION", captured.getvalue())


# ============================
# 4) Patrón observador
# ============================

class TestObservador(unittest.TestCase):

    def setUp(self):
        self._tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self._tmp.close()
        self.ctrl = MateriaControlador()
        self.ctrl._db = MateriaDB(self._tmp.name)
        self.ctrl._db.crear_tabla()

    def tearDown(self):
        os.unlink(self._tmp.name)

    def test_observer_recibe_evento_agregar(self):
        historial = HistorialObserver()
        self.ctrl.agregar_observador(historial)
        m = Materia(nivel="1", nombre="Mate", docente="Juan Perez", horas="4")
        self.ctrl.agregar(m)
        self.assertEqual(len(historial.historial), 1)
        self.assertEqual(historial.historial[0]["evento"], "agregar")

    def test_observer_recibe_evento_eliminar(self):
        historial = HistorialObserver()
        m = Materia(nivel="1", nombre="Mate", docente="Juan Perez", horas="4")
        self.ctrl.agregar(m)
        materias = self.ctrl.listar()
        self.ctrl.agregar_observador(historial)
        self.ctrl.eliminar(materias[0].id)
        eventos = [e["evento"] for e in historial.historial]
        self.assertIn("eliminar", eventos)

    def test_observer_recibe_evento_modificar(self):
        historial = HistorialObserver()
        m = Materia(nivel="1", nombre="Mate", docente="Juan Perez", horas="4")
        self.ctrl.agregar(m)
        materias = self.ctrl.listar()
        self.ctrl.agregar_observador(historial)
        materias[0].nombre = "Algebra"
        self.ctrl.modificar(materias[0])
        eventos = [e["evento"] for e in historial.historial]
        self.assertIn("modificar", eventos)

    def test_observer_recibe_evento_listar(self):
        historial = HistorialObserver()
        self.ctrl.agregar_observador(historial)
        self.ctrl.listar()
        self.assertEqual(len(historial.historial), 1)
        self.assertEqual(historial.historial[0]["evento"], "listar")

    def test_log_observer_imprime(self):
        captured = io.StringIO()
        sys.stdout = captured
        log_obs = LogObserver()
        self.ctrl.agregar_observador(log_obs)
        m = Materia(nivel="1", nombre="Mate", docente="Juan Perez", horas="4")
        self.ctrl.agregar(m)
        sys.stdout = sys.__stdout__
        self.assertIn("OBSERVER", captured.getvalue())
        self.assertIn("Mate", captured.getvalue())

    def test_eliminar_observador(self):
        historial = HistorialObserver()
        self.ctrl.agregar_observador(historial)
        self.ctrl.eliminar_observador(historial)
        m = Materia(nivel="1", nombre="Mate", docente="Juan Perez", horas="4")
        self.ctrl.agregar(m)
        self.assertEqual(len(historial.historial), 0)

    def test_historial_limpiar(self):
        historial = HistorialObserver()
        historial.actualizar("agregar", Materia(nombre="Mate"))
        self.assertEqual(len(historial.historial), 1)
        historial.limpiar()
        self.assertEqual(len(historial.historial), 0)


# ============================
# 2) MVC (controlador integrado)
# ============================

class TestControlador(unittest.TestCase):

    def setUp(self):
        self._tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self._tmp.close()
        self.ctrl = MateriaControlador()
        self.ctrl._db = MateriaDB(self._tmp.name)
        self.ctrl._db.crear_tabla()

    def tearDown(self):
        os.unlink(self._tmp.name)

    def test_validar_profesor_valido(self):
        self.assertTrue(MateriaControlador.validar_profesor("Juan Perez"))
        self.assertTrue(MateriaControlador.validar_profesor("Maria"))

    def test_validar_profesor_invalido(self):
        self.assertFalse(MateriaControlador.validar_profesor(""))
        self.assertFalse(MateriaControlador.validar_profesor("Juan123"))
        self.assertFalse(MateriaControlador.validar_profesor(" Juan"))

    def test_validar_horas_valido(self):
        self.assertTrue(MateriaControlador.validar_horas("4"))
        self.assertTrue(MateriaControlador.validar_horas("10"))
        self.assertTrue(MateriaControlador.validar_horas("1"))

    def test_validar_horas_invalido(self):
        self.assertFalse(MateriaControlador.validar_horas(""))
        self.assertFalse(MateriaControlador.validar_horas("abc"))
        self.assertFalse(MateriaControlador.validar_horas("4.5"))
        self.assertFalse(MateriaControlador.validar_horas("0"))

    def test_agregar_profesor_valido(self):
        m = Materia(nivel="1", nombre="Mate", docente="Juan Perez", horas="4")
        ok, _ = self.ctrl.agregar(m)
        self.assertTrue(ok)
        materias = self.ctrl.listar()
        self.assertEqual(len(materias), 1)
        self.assertEqual(materias[0].docente, "Juan Perez")

    def test_agregar_profesor_invalido_no_inserta(self):
        m = Materia(nivel="1", nombre="Mate", docente="Juan123", horas="4")
        ok, _ = self.ctrl.agregar(m)
        self.assertFalse(ok)
        self.assertEqual(self.ctrl.listar(), [])

    def test_agregar_horas_invalidas_no_inserta(self):
        m = Materia(nivel="1", nombre="Mate", docente="Juan Perez", horas="abc")
        ok, msg = self.ctrl.agregar(m)
        self.assertFalse(ok)
        self.assertIn("Horas", msg)

    def test_listar_vacio(self):
        self.assertEqual(self.ctrl.listar(), [])

    def test_eliminar(self):
        m = Materia(nivel="1", nombre="Mate", docente="Juan Perez", horas="4")
        self.ctrl.agregar(m)
        materias = self.ctrl.listar()
        self.ctrl.eliminar(materias[0].id)
        self.assertEqual(self.ctrl.listar(), [])

    def test_modificar_materia(self):
        m = Materia(nivel="1", nombre="Mate", docente="Juan Perez", horas="4")
        self.ctrl.agregar(m)
        materias = self.ctrl.listar()
        materias[0].nivel = "2"
        materias[0].nombre = "Algebra"
        materias[0].docente = "Maria Lopez"
        materias[0].horas = "6"
        self.ctrl.modificar(materias[0])
        result = self.ctrl.listar()
        self.assertEqual(result[0].nivel, "2")
        self.assertEqual(result[0].nombre, "Algebra")
        self.assertEqual(result[0].docente, "Maria Lopez")
        self.assertEqual(result[0].horas, "6")


if __name__ == "__main__":
    unittest.main()
