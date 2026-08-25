import io

import pytest
from app import create_app


@pytest.fixture
def client():
    application = create_app()
    application.config["TESTING"] = True
    with application.test_client() as c:
        yield c


def test_health_ok(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.get_json()["status"] == "ok"


def test_swagger_docs_ok(client):
    resp = client.get("/api/docs")
    assert resp.status_code == 200


def test_generate_returns_classes_code(client):
    resp = client.post(
        "/api/v1/generate",
        json={"inputText": "GET /api/users", "language": "csharp", "classesLang": "javascript"},
    )
    assert resp.status_code == 200
    data = resp.get_json()
    assert "controllerCode" in data
    assert "classesCode" in data
    assert "async function getUsers" in data["classesCode"]


def test_generate_legacy_alias(client):
    resp = client.post(
        "/api/generate",
        json={"inputText": "GET /api/users", "language": "csharp", "classesLang": "javascript"},
    )
    assert resp.status_code == 200
    assert "classesCode" in resp.get_json()


def test_generate_defaults_classes_lang_to_javascript(client):
    resp = client.post(
        "/api/v1/generate",
        json={"inputText": "GET /api/users", "language": "csharp"},
    )
    assert resp.status_code == 200
    data = resp.get_json()
    assert "classesCode" in data
    assert "async function" in data["classesCode"]


def test_generate_typescript_classes(client):
    resp = client.post(
        "/api/v1/generate",
        json={"inputText": "GET /api/users", "language": "csharp", "classesLang": "typescript"},
    )
    assert resp.status_code == 200
    data = resp.get_json()
    assert "Promise<void>" in data["classesCode"]


def test_generate_python_classes(client):
    resp = client.post(
        "/api/v1/generate",
        json={"inputText": "POST /api/users", "language": "java", "classesLang": "python"},
    )
    assert resp.status_code == 200
    data = resp.get_json()
    assert "import requests" in data["classesCode"]


def test_generate_invalid_classes_lang_returns_error(client):
    resp = client.post(
        "/api/v1/generate",
        json={"inputText": "GET /api/users", "language": "csharp", "classesLang": "cobol"},
    )
    assert resp.status_code in (400, 500)


def test_generate_response_includes_classes_lang(client):
    resp = client.post(
        "/api/v1/generate",
        json={"inputText": "GET /api/users", "language": "csharp", "classesLang": "java"},
    )
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["classesLang"] == "java"


def test_xml_to_html_json_success(client):
    resp = client.post(
        "/api/v1/xml-to-html",
        json={"xmlText": "<root><child>hi</child></root>"},
    )
    assert resp.status_code == 200
    data = resp.get_json()
    assert "html" in data
    assert "<!DOCTYPE html>" in data["html"]
    assert "<th>_</th>" in data["html"]
    assert "hi" in data["html"]


def test_xml_to_html_legacy_alias(client):
    resp = client.post(
        "/api/xml-to-html",
        json={"xmlText": "<root>hi</root>"},
    )
    assert resp.status_code == 200
    assert "hi" in resp.get_json()["html"]


def test_xml_to_html_missing_input_returns_400(client):
    resp = client.post("/api/v1/xml-to-html", json={})
    assert resp.status_code == 400
    assert "error" in resp.get_json()


def test_xml_to_html_invalid_xml_returns_400(client):
    resp = client.post("/api/v1/xml-to-html", json={"xmlText": "<root><x>"})
    assert resp.status_code == 400
    assert "error" in resp.get_json()


def test_xml_to_html_multipart_file(client):
    data = {
        "file": (io.BytesIO(b"<note><body>ok</body></note>"), "note.xml"),
    }
    resp = client.post(
        "/api/v1/xml-to-html",
        data=data,
        content_type="multipart/form-data",
    )
    assert resp.status_code == 200
    assert "ok" in resp.get_json()["html"]
