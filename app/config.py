import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    api_key: str
    k: int
    random_state: int
    max_actas: int
    distancia_sin_hidrante_m: float


def cargar_settings() -> Settings:
    """Lee la configuracion del entorno en cada llamada (permite cambiarla en las pruebas)."""
    return Settings(
        api_key=os.environ.get("ML_API_KEY", ""),
        k=int(os.environ.get("ML_K", "3")),
        random_state=int(os.environ.get("ML_RANDOM_STATE", "42")),
        max_actas=int(os.environ.get("ML_MAX_ACTAS", "20000")),
        distancia_sin_hidrante_m=float(os.environ.get("ML_DISTANCIA_SIN_HIDRANTE_M", "500")),
    )
