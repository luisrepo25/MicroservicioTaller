from typing import Literal

from pydantic import BaseModel, Field

NivelRiesgo = Literal["Bajo", "Medio", "Critico"]


class ActaEntrada(BaseModel):
    """Variables de una acta cerrada. Django las envia ya calculadas (el ML no las deriva)."""

    acta_id: int
    carga_fuego: float = Field(ge=0, description="MJ/m2, calculada por el backend (NB 58005)")
    riesgo_extintores: float = Field(
        ge=0, le=1, description="0 = vigente, 0.5 = vencido, 1 = no posee (mismo valor del scoring)"
    )
    fallas_electricas: bool
    rutas_obstruidas: bool
    distancia_hidrante_m: float | None = Field(
        default=None, ge=0, description="null = sin hidrante activo cercano"
    )
    scoring_riesgo: float = Field(ge=0, le=100, description="Solo se usa para nombrar los clusters")


class EjecutarClusteringEntrada(BaseModel):
    actas: list[ActaEntrada]


class ClusterActa(BaseModel):
    acta_id: int
    cluster_riesgo: NivelRiesgo


class ResumenCluster(BaseModel):
    cluster_riesgo: NivelRiesgo
    cantidad_actas: int
    scoring_promedio: float


class EjecutarClusteringSalida(BaseModel):
    k: int
    cantidad_actas: int
    coeficiente_silueta: float
    clusters: list[ClusterActa]
    resumen: list[ResumenCluster]
