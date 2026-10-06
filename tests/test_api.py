# tests/test_api.py
# Pruebas automatizadas para OpenDelegate v0.2.0
# Ejecutar con: pytest -v

import pytest
from fastapi.testclient import TestClient

from open_delegate import app

client = TestClient(app)


def test_raiz_devuelve_principios():
    """GET / debe devolver el nombre y los 5 principios."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["nombre"] == "OpenDelegate"
    assert len(data["principios"]) == 5
    assert "El usuario manda" in data["principios"]


def test_permisos_iniciales():
    """GET /permisos debe mostrar los permisos por defecto."""
    response = client.get("/permisos")
    assert response.status_code == 200
    data = response.json()
    assert len(data["permisos"]) >= 2
    recursos = [p["recurso"] for p in data["permisos"]]
    assert "tienda-ejemplo.com" in recursos
    assert "vuelos" in recursos


def test_solicitar_compra_dentro_del_limite():
    """POST /solicitar-compra con precio <= 100 debe crear la solicitud."""
    response = client.post(
        "/solicitar-compra",
        json={"producto": "teclado de prueba", "precio": 45, "tienda": "tienda-ejemplo.com"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["estado"] == "pendiente_aprobacion"
    assert data["producto"] == "teclado de prueba"
    assert data["agente_se_identifica_como"] == "open-delegate-v1 (IA)"


def test_solicitar_compra_supera_limite():
    """POST /solicitar-compra con precio > 100 debe devolver 403."""
    response = client.post(
        "/solicitar-compra",
        json={"producto": "monitor caro", "precio": 200, "tienda": "tienda-ejemplo.com"},
    )
    assert response.status_code == 403
    assert "limite" in response.json()["detail"].lower()


def test_solicitar_compra_tienda_sin_permiso():
    """POST /solicitar-compra en tienda no autorizada debe devolver 403."""
    response = client.post(
        "/solicitar-compra",
        json={"producto": "libro", "precio": 20, "tienda": "tienda-desconocida.com"},
    )
    assert response.status_code == 403
    assert "Sin permiso" in response.json()["detail"]


def test_aprobar_compra_genera_token():
    """POST /aprobar debe generar una credencial de un solo uso."""
    r1 = client.post(
        "/solicitar-compra",
        json={"producto": "raton", "precio": 30, "tienda": "tienda-ejemplo.com"},
    )
    assert r1.status_code == 200
    sol_id = r1.json()["id"]

    r2 = client.post("/aprobar", json={"solicitud_id": sol_id, "aprobado": True})
    assert r2.status_code == 200
    data = r2.json()
    assert data["estado"] == "aprobado"
    assert "credencial_generada" in data
    assert data["credencial_generada"]["tipo"] == "token_de_un_solo_uso"
    assert data["credencial_generada"]["contrasenas_reales"] is False


def test_auditoria_registra_eventos():
    """GET /auditoria debe devolver una lista de eventos."""
    response = client.get("/auditoria")
    assert response.status_code == 200
    data = response.json()
    assert "eventos" in data
    assert isinstance(data["eventos"], list)
