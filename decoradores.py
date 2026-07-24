import functools
import logging

logger = logging.getLogger(__name__)


def log_agregar(func):
    """Registra cuando se agrega un nuevo registro."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        resultado = func(*args, **kwargs)
        materia = kwargs.get("materia") or (args[1] if len(args) > 1 else None)
        nombre = materia.nombre if hasattr(materia, "nombre") else materia
        logger.info("INGRESO: Nueva materia '%s' registrada", nombre)
        return resultado
    return wrapper


def log_eliminar(func):
    """Registra cuando se elimina un registro."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        mi_id = kwargs.get("mi_id") or (args[1] if len(args) > 1 else "?")
        logger.info("ELIMINACION: Materia ID %s eliminada", mi_id)
        return func(*args, **kwargs)
    return wrapper


def log_modificar(func):
    """Registra cuando se actualiza un registro."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        resultado = func(*args, **kwargs)
        materia = kwargs.get("materia") or (args[1] if len(args) > 1 else None)
        nombre = materia.nombre if hasattr(materia, "nombre") else materia
        logger.info("ACTUALIZACION: Materia '%s' modificada", nombre)
        return resultado
    return wrapper
