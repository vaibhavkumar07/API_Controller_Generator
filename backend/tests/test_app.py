import io

import pytest
from app import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


def test_generate_returns_classes_code(client):
    resp = client.post(
        "/api/generate",
        json={"inputText": "GET /api/users", "language": "csharp", "classesLang": "javascript"},
    )
    assert resp.status_code == 200
    data = resp.get_json()
    assert "controllerCode" in data
    assert "classesCode" in data
    assert "async function getUsers" in data["classesCode"]


def test_generate_defaults_classes_lang_to_javascript(client):
    resp = client.post(
        "/api/generate",
        json={"inputText": "GET /api/users", "language": "csharp"},
    )
    assert resp.status_code == 200
    data = resp.get_json()
    assert "classesCode" in data
    assert "async function" in data["classesCode"]


def test_generate_typescript_classes(client):
    resp = client.post(
        "/api/generate",
        json={"inputText": "GET /api/users", "language": "csharp", "classesLang": "typescript"},
    )
    assert resp.status_code == 200
    data = resp.get_json()
    assert "Promise<void>" in data["classesCode"]


def test_generate_python_classes(client):
    resp = client.post(
        "/api/generate",
        json={"inputText": "POST /api/users", "language": "java", "classesLang": "python"},
    )
    assert resp.status_code == 200
    data = resp.get_json()
    assert "import requests" in data["classesCode"]


def test_generate_invalid_classes_lang_returns_error(client):
    resp = client.post(
        "/api/generate",
        json={"inputText": "GET /api/users", "language": "csharp", "classesLang": "cobol"},
    )
    assert resp.status_code in (400, 500)


def test_generate_response_includes_classes_lang(client):
    resp = client.post(
        "/api/generate",
        json={"inputText": "GET /api/users", "language": "csharp", "classesLang": "java"},
    )
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["classesLang"] == "java"


def test_xml_to_html_json_success(client):
    resp = client.post(
        "/api/xml-to-html",
        json={"xmlText": "<root><child>hi</child></root>"},
    )
    assert resp.status_code == 200
    data = resp.get_json()
    assert "html" in data
    assert "<!DOCTYPE html>" in data["html"]
    assert "child" in data["html"]
    assert "hi" in data["html"]


def test_xml_to_html_missing_input_returns_400(client):
    resp = client.post("/api/xml-to-html", json={})
    assert resp.status_code == 400
    assert "error" in resp.get_json()


def test_xml_to_html_invalid_xml_returns_400(client):
    resp = client.post("/api/xml-to-html", json={"xmlText": "<root><x>"})
    assert resp.status_code == 400
    assert "error" in resp.get_json()


def test_xml_to_html_multipart_file(client):
    data = {
        "file": (io.BytesIO(b"<note><body>ok</body></note>"), "note.xml"),
    }
    resp = client.post(
        "/api/xml-to-html",
        data=data,
        content_type="multipart/form-data",
    )
    assert resp.status_code == 200
    assert "ok" in resp.get_json()["html"]
