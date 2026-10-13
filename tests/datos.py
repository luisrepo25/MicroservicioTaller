"""Dataset sintetico fijo: tres grupos bien separados (bajo / medio / alto riesgo)."""

import numpy as np

from app.schemas import ActaEntrada

# (carga_fuego, riesgo_extintores, fallas, rutas_obstruidas, distancia_m, scoring)
PERFILES = {
    "bajo": (20.0, 0.0, False, False, 40.0, 8.0),
    "medio": (400.0, 0.5, False, True, 250.0, 50.0),
    "alto": (900.0, 1.0, True, True, 480.0, 92.0),
}


def generar_actas(por_grupo: int = 20) -> list[ActaEntrada]:
    rng = np.random.default_rng(7)
    actas = []
    for carga, ext, fallas, rutas, dist, score in PERFILES.values():
        for _ in range(por_grupo):
            actas.append(
                ActaEntrada(
                    acta_id=len(actas) + 1,
                    carga_fuego=max(0.0, carga + rng.normal(0, 5)),
                    riesgo_extintores=ext,
                    fallas_electricas=fallas,
                    rutas_obstruidas=rutas,
                    distancia_hidrante_m=max(0.0, dist + rng.normal(0, 5)),
                    scoring_riesgo=float(np.clip(score + rng.normal(0, 1), 0, 100)),
                )
            )
    return actas
