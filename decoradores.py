import functools
import datetime


def log_agregar(func):
    """Registra cuando se agrega un nuevo registro."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        resultado = func(*args, **kwargs)
        momento = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        materia = kwargs.get("materia") or (args[1] if len(args) > 1 else None)
        nombre = materia.nombre if hasattr(materia, "nombre") else materia
        print(f"[{momento}] INGRESO: Nueva materia '{nombre}' registrada")
        return resultado
    return wrapper


def log_eliminar(func):
    """Registra cuando se elimina un registro."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        momento = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        mi_id = kwargs.get("mi_id") or (args[1] if len(args) > 1 else "?")
        print(f"[{momento}] ELIMINACION: Materia ID {mi_id} eliminada")
        return func(*args, **kwargs)
    return wrapper


def log_modificar(func):
    """Registra cuando se actualiza un registro."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        resultado = func(*args, **kwargs)
        momento = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        materia = kwargs.get("materia") or (args[1] if len(args) > 1 else None)
        nombre = materia.nombre if hasattr(materia, "nombre") else materia
        print(f"[{momento}] ACTUALIZACION: Materia '{nombre}' modificada")
        return resultado
    return wrapper
