# Python Intermedio - Gestion de Materias

Aplicacion de escritorio (Tkinter + SQLite) que gestiona materias academicas, aplicando los 4 temas del curso.

---

## 1) POO (Programacion Orientada a Objetos)

**Archivo:** `modelo.py`

La clase `Materia` encapsula los atributos de una materia (nivel, nombre, docente, horas) y encapsula los comportamientos asociados:

- **Constructor** con valores por defecto
- **`__eq__`**: compara dos materias por atributos (no por identidad)
- **`__repr__`**: representacion legible para depuracion
- **`a_tupla()`**: convierte el objeto a tupla para insercion en SQLite
- **`desde_fila()`** (`@classmethod`): fabrica un objeto `Materia` desde una fila de la base de datos

La clase se usa como modelo de datos en toda la arquitectura MVC.

---

## 2) MVC (Modelo-Vista-Controlador)

La aplicacion separa responsabilidades en 3 capas:

### Modelo (`modelo.py`)
Representa los datos (`Materia`) y su persistencia. No conocce la interfaz ni la logica de negocio.

### Vista (`vista.py`)
Interfaz grafica con Tkinter. Crea el formulario, tabla (Treeview), botones y barra de estado. **No valida ni accede a la base directamente**; delega todo al controlador.

Funciones clave de la vista:
- `agregar()`: valida campos obligatorios, crea `Materia`, llama a `ctrl.agregar()`
- `modificar()`: selecciona fila del Treeview, actualiza via `ctrl.modificar()`
- `eliminar()`: confirma con el usuario, llama a `ctrl.eliminar()`
- `actualizar_tabla()`: refresca el Treeview desde `ctrl.listar()`

### Controlador (`controlador.py`)
`MateriaControlador` orquesta las operaciones CRUD:
- Recibe peticiones de la vista
- Valida reglas de negocio (nombre del profesor con regex, horas > 0)
- Inserta/actualiza/borra en la base via `MateriaDB`
- Notifica a los observadores registrados

```
Vista  -->  Controlador  -->  Modelo (MateriaDB / SQLite)
  ^              |
  |              v
  +-------- Observadores (log)
```

---

## 3) Decorador (Registro de log)

**Archivo:** `decoradores.py`

Tres decoradores envuelven funciones del controlador para registrar cada operacion en el log **sin modificar la logica original**:

```python
@log_agregar        # registra: "INGRESO: Nueva materia 'X' registrada"
def agregar(self, materia): ...

@log_eliminar       # registra: "ELIMINACION: Materia ID X eliminada"
def eliminar(self, mi_id): ...

@log_modificar      # registra: "ACTUALIZACION: Materia 'X' modificada"
def modificar(self, materia): ...
```

**Mecanismo interno:**
1. Cada decorador usa `@functools.wraps` para conservar el `__name__` y `__doc__` de la funcion original
2. Extrae el argumento relevante de `args` o `kwargs` (el objeto `Materia` o el `id`)
3. Ejecuta la funcion original con `func(*args, **kwargs)`
4. Registra el evento via `logging.getLogger(__name__).info(...)`

**Ventaja:** El controlador no sabe que esta siendo decorado. Se puede agregar/quitar logging cambiando solo los decoradores.

---

## 4) Patron Observador (Registro de log)

**Archivo:** `observador.py`

Implementa el patron Observer (Tema/Concreto) para notificar a multiples observadores ante cada operacion CRUD. Un solo sistema, sin duplicaciones.

### Estructura del patron

| Concepto       | Clase               | Rol                                      |
|----------------|----------------------|------------------------------------------|
| **Tema**       | `Tema` / `TemaConcreto` | Sujeto observable, mantiene lista de observadores |
| **Observador** | `Observador` / `LogObserver` / `HistorialObserver` | Reaccionan ante cambios de estado via `update()` |
| **Subject**    | `Subject`            | Wrapper que adapta TemaConcreto al controlador |

### Flujo en el controlador

```
1. Vista llama ctrl.agregar(materia)
2. Controlador ejecuta la operacion CRUD
3. Controlador llama self.notificar("agregar", materia)
4. Subject construye un dict estado y llama self._tema.set_estado(estado)
5. TemaConcreto recorre sus observadores y llama update() a cada uno
6. Cada observador lee el estado con get_estado() y actua
```

**Una sola cadena de notificacion**, sin duplicaciones.

### Observadores implementados

- **`LogObserver`**: registra cada evento (agregar/eliminar/modificar/listar) via `logging.info` con prefijo `[Observer]`. Tambien almacena el ultimo estado en `self.estado`.
- **`HistorialObserver`**: acumula todos los eventos en una lista en memoria (`self.historial`).

### Registro en la aplicacion

En `vista.py:11`:
```python
ctrl = MateriaControlador()
ctrl.agregar_observador(LogObserver())  # Subject le asigna el tema
```

**Ventaja:** Se pueden agregar multiples observadores (log, historial, notificaciones, etc.) sin modificar el controlador.

---

## Patrones adicionales (en `patrones.py`)

### Singleton - `MateriaDB`
Asegura una unica instancia de la conexion a la base de datos SQLite. Cualquier `MateriaDB(path)` retorna la misma instancia.

### Factory - `MateriaFactory`
Crea objetos `MateriaBasica`, `MateriaIntermedia` o `MateriaAvanzada` segun el nivel (1-2, 3, 4-5). Registra clases con `registrar(nivel, clase)` y crea con `crear(nivel, **kwargs)`.

### Adapter - `CalendarioAdapter`
Adapta un sistema externo de calendario (`CalendarioExterno`) al formato que espera el sistema de materias (`FormatoMaterias`), convirtiendo eventos con `duracion_min` a horas.

---

## Ejecucion

```bash
python main.py
```

## Tests

```bash
python -m pytest test_materias.py -v
# o
python -m unittest test_materias -v
```
