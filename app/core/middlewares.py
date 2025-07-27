from functools import wraps

from app.models.auth import NivelAcesso

def requer_acesso(nivel_requerido: NivelAcesso):
    def decorator(f):
        @wraps(f)
        def wrapper(usuario_atual, *args, **kwargs):
            if usuario_atual.nivel_acesso.value >= nivel_requerido.value:
                return f(usuario_atual, *args, **kwargs)
            raise PermissionError("Acesso negado!")
        return wrapper
    return decorator