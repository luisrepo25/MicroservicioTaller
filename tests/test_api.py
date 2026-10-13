import pytest
from fastapi.testclient import TestClient

from app.main import app
from tests.datos import generar_actas

URL = "/clustering/ejecutar"


@pytest.fixture(autouse=True)
def _api_key(monkeypatch):
    monkeypatch.setenv("ML_API_KEY", "secreta")


@pytest.fixture
def client():
    return TestClient(app)


def _cuerpo(actas=None):
    actas = actas if actas is not None else generar_actas()
    return {"actas": [a.model_dump() for a in actas]}


def test_health_no_exige_clave(client):
    assert client.get("/health").json() == {"estado": "ok"}


def test_sin_api_key_responde_401(client):
    assert client.post(URL, json=_cuerpo()).status_code == 401


def test_api_key_incorrecta_responde_401(client):
    assert client.post(URL, json=_cuerpo(), headers={"X-API-Key": "otra"}).status_code == 401


def test_sin_clave_configurada_nadie_entra(client, monkeypatch):
    monkeypatch.setenv("ML_API_KEY", "")
    assert client.post(URL, json=_cuerpo(), headers={"X-API-Key": ""}).status_code == 401


def test_ejecuta_clustering(client):
    r = client.post(URL, json=_cuerpo(), headers={"X-API-Key": "secreta"})
    assert r.status_code == 200
    datos = r.json()
    assert datos["k"] == 3
    assert datos["cantidad_actas"] == 60
    assert len(datos["clusters"]) == 60
    assert -1 <= datos["coeficiente_silueta"] <= 1


def test_pocas_actas_responde_422(client):
    r = client.post(URL, json=_cuerpo(generar_actas(por_grupo=1)), headers={"X-API-Key": "secreta"})
    assert r.status_code == 422


def test_dato_invalido_responde_422(client):
    cuerpo = _cuerpo()
    cuerpo["actas"][0]["riesgo_extintores"] = 7
    r = client.post(URL, json=cuerpo, headers={"X-API-Key": "secreta"})
    assert r.status_code == 422
