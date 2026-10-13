import pytest

from app.config import Settings
from app.services import clustering
from tests.datos import generar_actas

SETTINGS = Settings(
    api_key="x", k=3, random_state=42, max_actas=1000, distancia_sin_hidrante_m=500.0
)


def test_separa_los_tres_grupos_y_los_nombra_por_severidad():
    resultado = clustering.ejecutar_clustering(generar_actas(), SETTINGS)
    por_acta = {c.acta_id: c.cluster_riesgo for c in resultado.clusters}

    assert {por_acta[i] for i in range(1, 21)} == {"Bajo"}
    assert {por_acta[i] for i in range(21, 41)} == {"Medio"}
    assert {por_acta[i] for i in range(41, 61)} == {"Critico"}
    assert [r.cluster_riesgo for r in resultado.resumen] == ["Bajo", "Medio", "Critico"]
    assert all(r.cantidad_actas == 20 for r in resultado.resumen)


def test_silueta_es_reproducible_y_alta_con_grupos_separados():
    primera = clustering.ejecutar_clustering(generar_actas(), SETTINGS)
    segunda = clustering.ejecutar_clustering(generar_actas(), SETTINGS)

    assert primera.coeficiente_silueta == segunda.coeficiente_silueta
    assert primera.coeficiente_silueta > 0.7
    assert primera.coeficiente_silueta <= 1.0


def test_acta_sin_hidrante_usa_la_distancia_por_defecto():
    actas = generar_actas()
    actas[0] = actas[0].model_copy(update={"distancia_hidrante_m": None})
    matriz = clustering.construir_matriz(actas, 500.0)
    assert matriz[0][4] == 500.0


def test_rechaza_pocas_actas():
    with pytest.raises(clustering.ClusteringError, match="al menos 4"):
        clustering.ejecutar_clustering(generar_actas(por_grupo=1), SETTINGS)


def test_rechaza_acta_id_repetido():
    actas = generar_actas()
    actas[1] = actas[1].model_copy(update={"acta_id": actas[0].acta_id})
    with pytest.raises(clustering.ClusteringError, match="repetidos"):
        clustering.ejecutar_clustering(actas, SETTINGS)


def test_rechaza_actas_identicas():
    base = generar_actas()[0]
    actas = [base.model_copy(update={"acta_id": i}) for i in range(1, 11)]
    with pytest.raises(clustering.ClusteringError):
        clustering.ejecutar_clustering(actas, SETTINGS)


def test_rechaza_exceso_de_actas():
    chico = Settings(
        api_key="x", k=3, random_state=42, max_actas=10, distancia_sin_hidrante_m=500.0
    )
    with pytest.raises(clustering.ClusteringError, match="mas de 10"):
        clustering.ejecutar_clustering(generar_actas(), chico)
