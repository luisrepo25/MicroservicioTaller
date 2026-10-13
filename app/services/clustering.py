"""Capa de negocio: K-Means de riesgo (RF-17). No conoce HTTP ni la base de datos."""

import numpy as np
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler

from app.config import Settings
from app.schemas import (
    ActaEntrada,
    ClusterActa,
    EjecutarClusteringSalida,
    ResumenCluster,
)

# Orden de severidad: el cluster de menor scoring promedio es 'Bajo', el de mayor 'Critico'.
NOMBRES_K3 = ["Bajo", "Medio", "Critico"]


class ClusteringError(Exception):
    """Datos insuficientes o degenerados para agrupar (la ruta responde 422)."""


def construir_matriz(actas: list[ActaEntrada], distancia_sin_hidrante_m: float) -> np.ndarray:
    """Una fila por acta con las 5 variables de inspeccion (las mismas del scoring)."""
    return np.array(
        [
            [
                a.carga_fuego,
                a.riesgo_extintores,
                float(a.fallas_electricas),
                float(a.rutas_obstruidas),
                (
                    a.distancia_hidrante_m
                    if a.distancia_hidrante_m is not None
                    else distancia_sin_hidrante_m
                ),
            ]
            for a in actas
        ],
        dtype=float,
    )


def _validar(actas: list[ActaEntrada], settings: Settings) -> None:
    if settings.k != len(NOMBRES_K3):
        raise ClusteringError(f"Solo se soporta k={len(NOMBRES_K3)} (Bajo/Medio/Critico).")
    if len(actas) > settings.max_actas:
        raise ClusteringError(f"Se recibieron mas de {settings.max_actas} actas.")
    if len(actas) <= settings.k:
        raise ClusteringError(f"Se necesitan al menos {settings.k + 1} actas cerradas.")
    if len({a.acta_id for a in actas}) != len(actas):
        raise ClusteringError("Hay acta_id repetidos.")


def _nombrar_clusters(etiquetas: np.ndarray, scorings: np.ndarray, k: int) -> dict[int, str]:
    """Ordena los clusters por scoring promedio ascendente y les asigna Bajo/Medio/Critico."""
    promedios = {c: scorings[etiquetas == c].mean() for c in range(k)}
    orden = sorted(promedios, key=promedios.get)
    return {cluster: NOMBRES_K3[pos] for pos, cluster in enumerate(orden)}


def ejecutar_clustering(actas: list[ActaEntrada], settings: Settings) -> EjecutarClusteringSalida:
    _validar(actas, settings)

    matriz = StandardScaler().fit_transform(
        construir_matriz(actas, settings.distancia_sin_hidrante_m)
    )
    modelo = KMeans(n_clusters=settings.k, n_init=10, random_state=settings.random_state)
    etiquetas = modelo.fit_predict(matriz)

    if len(set(etiquetas)) < settings.k:
        raise ClusteringError(
            "Las actas son demasiado parecidas entre si para formar 3 grupos distintos."
        )

    scorings = np.array([a.scoring_riesgo for a in actas], dtype=float)
    nombres = _nombrar_clusters(etiquetas, scorings, settings.k)

    silueta = round(float(silhouette_score(matriz, etiquetas)), 3)
    clusters = [
        ClusterActa(acta_id=a.acta_id, cluster_riesgo=nombres[int(e)])
        for a, e in zip(actas, etiquetas, strict=True)
    ]
    resumen = [
        ResumenCluster(
            cluster_riesgo=nombres[c],
            cantidad_actas=int((etiquetas == c).sum()),
            scoring_promedio=round(float(scorings[etiquetas == c].mean()), 2),
        )
        for c in sorted(nombres, key=lambda c: NOMBRES_K3.index(nombres[c]))
    ]
    return EjecutarClusteringSalida(
        k=settings.k,
        cantidad_actas=len(actas),
        coeficiente_silueta=silueta,
        clusters=clusters,
        resumen=resumen,
    )
