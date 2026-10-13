# Microservicio de clustering de riesgo (Fase 5, RF-17)

Servicio interno, **sin estado y sin acceso a la base de datos**. El backend Django le envía las actas cerradas en JSON y recibe el cluster de cada una. Aplica `StandardScaler` + K-Means (k=3, `n_init=10`, `random_state` fijo) y calcula el coeficiente de silueta.

## Contrato

`POST /clustering/ejecutar` — cabecera `X-API-Key` obligatoria.

```json
{ "actas": [{
    "acta_id": 1, "carga_fuego": 83.61, "riesgo_extintores": 0.5,
    "fallas_electricas": false, "rutas_obstruidas": true,
    "distancia_hidrante_m": 120.5, "scoring_riesgo": 41.2 }] }
```

- `riesgo_extintores`: 0 vigente · 0.5 vencido · 1 no posee (el mismo valor que usa `calcular_scoring_riesgo`; Django lo calcula, el ML no duplica la regla).
- `distancia_hidrante_m: null` → se asume `ML_DISTANCIA_SIN_HIDRANTE_M` (500 m, igual que `D_MAX`).
- `scoring_riesgo` **no entra al modelo**: solo sirve para nombrar los clusters (menor promedio → `Bajo`, medio → `Medio`, mayor → `Critico`).

Respuesta 200: `k`, `cantidad_actas`, `coeficiente_silueta` (3 decimales, cabe en `NUMERIC(4,3)`), `clusters[{acta_id, cluster_riesgo}]` y `resumen` por cluster.
Errores: `401` clave inválida · `422` menos de k+1 actas, `acta_id` repetidos, actas idénticas, exceso de actas o dato fuera de rango.

`GET /health` — sin clave.

## Desarrollo

```
cp .env.example .env
docker compose up          # http://localhost:8001/docs
docker compose run --rm ml pytest -q
docker compose run --rm ml sh -c "ruff check . && black --check ."
```
