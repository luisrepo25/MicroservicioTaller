from fastapi import APIRouter, Depends, HTTPException, status

from app.config import cargar_settings
from app.schemas import EjecutarClusteringEntrada, EjecutarClusteringSalida
from app.security import exigir_api_key
from app.services import clustering

router = APIRouter()


@router.get("/health")
def health() -> dict[str, str]:
    return {"estado": "ok"}


@router.post(
    "/clustering/ejecutar",
    response_model=EjecutarClusteringSalida,
    dependencies=[Depends(exigir_api_key)],
)
def ejecutar_clustering(entrada: EjecutarClusteringEntrada) -> EjecutarClusteringSalida:
    try:
        return clustering.ejecutar_clustering(entrada.actas, cargar_settings())
    except clustering.ClusteringError as exc:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, str(exc)) from exc
