from fastapi.testclient import TestClient

from api import api

client = TestClient(api)


def test_menu_endpoint():
    response = client.get("/api/menu")

    assert response.status_code == 200
    data = response.json()
    assert data["asistente"] == "Asistente Virtual Alcaldia"
    assert "impuesto predial" in data["temas"]


def test_chat_endpoint_general_question():
    response = client.post("/api/chat", json={"pregunta": "ayuda"})

    assert response.status_code == 200
    assert "Puedo orientarte" in response.json()["respuesta"]


def test_chat_endpoint_rejects_empty_question():
    response = client.post("/api/chat", json={"pregunta": ""})

    assert response.status_code == 422
