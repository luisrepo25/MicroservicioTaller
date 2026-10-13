import hmac

from fastapi import Header, HTTPException, status

from app.config import cargar_settings


def exigir_api_key(x_api_key: str | None = Header(default=None)) -> None:
    """El servicio es interno: solo el backend Django, con la clave compartida, puede llamarlo."""
    esperada = cargar_settings().api_key
    if not esperada or x_api_key is None or not hmac.compare_digest(x_api_key, esperada):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "API key invalida o ausente.")
