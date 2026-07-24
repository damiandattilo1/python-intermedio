import logging
import os
import tempfile
import unittest

from modelo import Materia
from patrones import MateriaDB, MateriaFactory, CalendarioExterno, CalendarioAdapter, FormatoMateriasDirecto
from patrones import MateriaBasica, MateriaIntermedia, MateriaAvanzada
from observador import TemaConcreto, ConcreteObserverA, ConcreteObserverB
from controlador import MateriaControlador
from decoradores import log_agregar, log_eliminar, log_modificar
from observador import Subject, LogObserver, HistorialObserver


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
        self.assertEqual(m.horas, 4)
        self.assertIsInstance(m.horas, int)

    def test_creacion_con_valores(self):
        m = Materia(id=1, nivel="3", nombre="Algebra", docente="Juan Perez", horas=6)
        self.assertEqual(m.id, 1)
        self.assertEqual(m.nivel, "3")
        self.assertEqual(m.nombre, "Algebra")
        self.assertEqual(m.docente, "Juan Perez")
        self.assertEqual(m.horas, 6)
        self.assertIsInstance(m.horas, int)

    def test_creacion_horas_desde_string(self):
        m = Materia(horas="6")
        self.assertEqual(m.horas, 6)
        self.assertIsInstance(m.horas, int)

    def test_equality(self):
        a = Materia(nivel="1", nombre="Mate", docente="Juan", horas=4)
        b = Materia(nivel="1", nombre="Mate", docente="Juan", horas=4)
        c = Materia(nivel="2", nombre="Fisica", docente="Ana", horas=3)
        self.assertEqual(a, b)
        self.assertNotEqual(a, c)

    def test_a_tupla(self):
        m = Materia(nivel="2", nombre="Fisica", docente="Ana", horas=3)
        self.assertEqual(m.a_tupla(), ("2", "Fisica", "Ana", 3))

    def test_desde_fila(self):
        fila = (5, "1", "Mate", "Juan", 4)
        m = Materia.desde_fila(fila)
        self.assertEqual(m.id, 5)
        self.assertEqual(m.nombre, "Mate")
        self.assertEqual(m.horas, 4)
        self.assertIsInstance(m.horas, int)

    def test_repr(self):
        m = Materia(id=1, nivel="1", nombre="Mate", docente="Juan", horas=4)
        self.assertIn("Mate", repr(m))


# ============================
# PATRÓN SINGLETON
# ============================

class TestSingleton(unittest.TestCase):

    def setUp(self):
        self._tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self._tmp.close()

    def tearDown(self):
        MateriaDB.instancia = None
        os.unlink(self._tmp.name)

    def test_misma_instancia(self):
        db1 = MateriaDB(self._tmp.name)
        db2 = MateriaDB(self._tmp.name)
        self.assertIs(db1, db2)

    def test_instancia_comparte_estado(self):
        db1 = MateriaDB(self._tmp.name)
        db1.crear_tabla()
        m = Materia(nivel="1", nombre="Mate", docente="Juan", horas=4)
        db1.insertar(m)

        db2 = MateriaDB(self._tmp.name)
        materias = db2.obtener_todos()
        self.assertEqual(len(materias), 1)

    def test_singleton_con_diferentes_paths(self):
        db1 = MateriaDB(self._tmp.name)
        db2 = MateriaDB("/tmp/otra.db")
        self.assertIs(db1, db2)


# ============================
# PATRÓN FACTORY
# ============================

class TestFactory(unittest.TestCase):

    def test_crear_basica(self):
        m = MateriaFactory.crear("1", nombre="Mate", docente="Juan", horas=4)
        self.assertIsInstance(m, MateriaBasica)
        self.assertEqual(m.tipo, "Basica")
        self.assertEqual(m.nombre, "Mate")

    def test_crear_intermedia(self):
        m = MateriaFactory.crear("3", nombre="Quimica", docente="Ana", horas=5)
        self.assertIsInstance(m, MateriaIntermedia)
        self.assertEqual(m.tipo, "Intermedia")

    def test_crear_avanzada(self):
        m = MateriaFactory.crear("5", nombre="Calculo", docente="Pedro", horas=6)
        self.assertIsInstance(m, MateriaAvanzada)
        self.assertEqual(m.tipo, "Avanzada")

    def test_crear_nivel_default_basica(self):
        m = MateriaFactory.crear("2", nombre="Fisica", docente="Luis")
        self.assertIsInstance(m, MateriaBasica)

    def test_descripcion_basica(self):
        m = MateriaFactory.crear("1", nombre="Mate", docente="Juan")
        self.assertIn("Basica", m.descripcion())
        self.assertIn("Mate", m.descripcion())

    def test_descripcion_avanzada(self):
        m = MateriaFactory.crear("5", nombre="Calculo", docente="Pedro", horas=6)
        desc = m.descripcion()
        self.assertIn("Avanzada", desc)
        self.assertIn("6hs", desc)


# ============================
# PATRÓN ADAPTER
# ============================

class TestAdapter(unittest.TestCase):

    def test_adapter_calendario(self):
        calendario = CalendarioExterno()
        adapter = CalendarioAdapter(calendario)
        resultado = adapter.listar_materias_formateadas()
        self.assertEqual(len(resultado), 2)
        self.assertEqual(resultado[0]["nombre"], "Clase de Matematica")
        self.assertEqual(resultado[0]["horas"], 1)

    def test_adapter_directo(self):
        materias = [Materia(nombre="Mate", nivel="1", horas=4)]
        adapter = FormatoMateriasDirecto(materias)
        resultado = adapter.listar_materias_formateadas()
        self.assertEqual(len(resultado), 1)
        self.assertEqual(resultado[0]["nombre"], "Mate")
        self.assertEqual(resultado[0]["horas"], 4)

    def test_adapter_formato_compatido(self):
        calendario = CalendarioExterno()
        adapter = CalendarioAdapter(calendario)
        self.assertTrue(hasattr(adapter, "listar_materias_formateadas"))

    def test_formato_materias_directo_herencia(self):
        from patrones import FormatoMaterias
        adapter = FormatoMateriasDirecto([])
        self.assertIsInstance(adapter, FormatoMaterias)


# ============================
# PATRÓN OBSERVER (Tema/Concreto)
# ============================

class TestObserverCurso(unittest.TestCase):

    def test_tema_concreto_notifica(self):
        tema = TemaConcreto()
        observer = ConcreteObserverA(tema)
        tema.set_estado({"evento": "agregar", "nombre": "Mate"})
        self.assertEqual(observer.estado["evento"], "agregar")

    def test_dos_observers_notificados(self):
        tema = TemaConcreto()
        obs_a = ConcreteObserverA(tema)
        obs_b = ConcreteObserverB(tema)
        tema.set_estado({"evento": "eliminar", "id": 1})
        self.assertEqual(obs_a.estado["evento"], "eliminar")
        self.assertEqual(len(obs_b.historial), 1)

    def test_historial_observer(self):
        tema = TemaConcreto()
        obs_b = ConcreteObserverB(tema)
        tema.set_estado({"evento": "modificar", "nombre": "Algebra"})
        tema.set_estado({"evento": "listar", "cantidad": 5})
        self.assertEqual(len(obs_b.historial), 2)

    def test_quitar_observer(self):
        tema = TemaConcreto()
        obs_a = ConcreteObserverA(tema)
        tema.quitar(obs_a)
        tema.set_estado({"evento": "agregar", "nombre": "Mate"})
        self.assertIsNone(obs_a.estado)


# ============================
# 3) DECORADORES
# ============================

class TestDecoradores(unittest.TestCase):

    def setUp(self):
        self._tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self._tmp.close()
        self.ctrl = MateriaControlador()
        from patrones import MateriaDB as SingletonDB
        MateriaDB.instancia = None
        self.ctrl._db = SingletonDB(self._tmp.name)
        self.ctrl._db.crear_tabla()

    def tearDown(self):
        MateriaDB.instancia = None
        os.unlink(self._tmp.name)

    def test_log_agregar_imprime(self):
        m = Materia(nivel="1", nombre="Mate", docente="Juan Perez", horas=4)
        with self.assertLogs("decoradores", level="INFO") as cm:
            self.ctrl.agregar(m)
        self.assertTrue(any("INGRESO" in msg for msg in cm.output))
        self.assertTrue(any("Mate" in msg for msg in cm.output))

    def test_log_eliminar_imprime(self):
        m = Materia(nivel="1", nombre="Mate", docente="Juan Perez", horas=4)
        self.ctrl.agregar(m)
        materias = self.ctrl.listar()
        with self.assertLogs("decoradores", level="INFO") as cm:
            self.ctrl.eliminar(materias[0].id)
        self.assertTrue(any("ELIMINACION" in msg for msg in cm.output))

    def test_log_modificar_imprime(self):
        m = Materia(nivel="1", nombre="Mate", docente="Juan Perez", horas=4)
        self.ctrl.agregar(m)
        materias = self.ctrl.listar()
        materias[0].nombre = "Algebra"
        with self.assertLogs("decoradores", level="INFO") as cm:
            self.ctrl.modificar(materias[0])
        self.assertTrue(any("ACTUALIZACION" in msg for msg in cm.output))
        self.assertTrue(any("Algebra" in msg for msg in cm.output))



# ============================
# 4) PATRÓN OBSERVER (legacy)
# ============================

class TestObservadorLegacy(unittest.TestCase):

    def setUp(self):
        self._tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self._tmp.close()
        self.ctrl = MateriaControlador()
        from patrones import MateriaDB as SingletonDB
        MateriaDB.instancia = None
        self.ctrl._db = SingletonDB(self._tmp.name)
        self.ctrl._db.crear_tabla()

    def tearDown(self):
        MateriaDB.instancia = None
        os.unlink(self._tmp.name)

    def test_observer_recibe_evento_agregar(self):
        historial = HistorialObserver()
        self.ctrl.agregar_observador(historial)
        m = Materia(nivel="1", nombre="Mate", docente="Juan Perez", horas=4)
        self.ctrl.agregar(m)
        self.assertEqual(len(historial.historial), 1)
        self.assertEqual(historial.historial[0]["evento"], "agregar")

    def test_observer_recibe_evento_eliminar(self):
        historial = HistorialObserver()
        m = Materia(nivel="1", nombre="Mate", docente="Juan Perez", horas=4)
        self.ctrl.agregar(m)
        materias = self.ctrl.listar()
        self.ctrl.agregar_observador(historial)
        self.ctrl.eliminar(materias[0].id)
        eventos = [e["evento"] for e in historial.historial]
        self.assertIn("eliminar", eventos)

    def test_observer_recibe_evento_modificar(self):
        historial = HistorialObserver()
        m = Materia(nivel="1", nombre="Mate", docente="Juan Perez", horas=4)
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
        log_obs = LogObserver()
        self.ctrl.agregar_observador(log_obs)
        m = Materia(nivel="1", nombre="Mate", docente="Juan Perez", horas=4)
        with self.assertLogs("observador", level="INFO") as cm:
            self.ctrl.agregar(m)
        self.assertTrue(any("OBSERVER" in msg for msg in cm.output))
        self.assertTrue(any("Mate" in msg for msg in cm.output))

    def test_eliminar_observador(self):
        historial = HistorialObserver()
        self.ctrl.agregar_observador(historial)
        self.ctrl.eliminar_observador(historial)
        m = Materia(nivel="1", nombre="Mate", docente="Juan Perez", horas=4)
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
        from patrones import MateriaDB as SingletonDB
        MateriaDB.instancia = None
        self.ctrl._db = SingletonDB(self._tmp.name)
        self.ctrl._db.crear_tabla()

    def tearDown(self):
        MateriaDB.instancia = None
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
        self.assertTrue(MateriaControlador.validar_horas(4))
        self.assertTrue(MateriaControlador.validar_horas("10"))

    def test_validar_horas_invalido(self):
        self.assertFalse(MateriaControlador.validar_horas(""))
        self.assertFalse(MateriaControlador.validar_horas("abc"))
        self.assertFalse(MateriaControlador.validar_horas("4.5"))
        self.assertFalse(MateriaControlador.validar_horas("0"))
        self.assertFalse(MateriaControlador.validar_horas(0))
        self.assertFalse(MateriaControlador.validar_horas(-3))

    def test_agregar_profesor_valido(self):
        m = Materia(nivel="1", nombre="Mate", docente="Juan Perez", horas=4)
        ok, _ = self.ctrl.agregar(m)
        self.assertTrue(ok)
        materias = self.ctrl.listar()
        self.assertEqual(len(materias), 1)
        self.assertEqual(materias[0].docente, "Juan Perez")
        self.assertEqual(materias[0].horas, 4)

    def test_agregar_profesor_invalido_no_inserta(self):
        m = Materia(nivel="1", nombre="Mate", docente="Juan123", horas=4)
        ok, _ = self.ctrl.agregar(m)
        self.assertFalse(ok)
        self.assertEqual(self.ctrl.listar(), [])

    def test_agregar_horas_invalidas_no_inserta(self):
        m = Materia(nivel="1", nombre="Mate", docente="Juan Perez", horas=0)
        ok, msg = self.ctrl.agregar(m)
        self.assertFalse(ok)
        self.assertIn("Horas", msg)

    def test_listar_vacio(self):
        self.assertEqual(self.ctrl.listar(), [])

    def test_eliminar(self):
        m = Materia(nivel="1", nombre="Mate", docente="Juan Perez", horas=4)
        self.ctrl.agregar(m)
        materias = self.ctrl.listar()
        self.ctrl.eliminar(materias[0].id)
        self.assertEqual(self.ctrl.listar(), [])

    def test_modificar_materia(self):
        m = Materia(nivel="1", nombre="Mate", docente="Juan Perez", horas=4)
        self.ctrl.agregar(m)
        materias = self.ctrl.listar()
        materias[0].nivel = "2"
        materias[0].nombre = "Algebra"
        materias[0].docente = "Maria Lopez"
        materias[0].horas = 6
        self.ctrl.modificar(materias[0])
        result = self.ctrl.listar()
        self.assertEqual(result[0].nivel, "2")
        self.assertEqual(result[0].nombre, "Algebra")
        self.assertEqual(result[0].docente, "Maria Lopez")
        self.assertEqual(result[0].horas, 6)
        self.assertIsInstance(result[0].horas, int)


if __name__ == "__main__":
    unittest.main()
