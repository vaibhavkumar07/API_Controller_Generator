import pytest
from generator import generate_classes


def ep(method, path):
    return [{"method": method, "path": path}]


class TestGenerateClassesJS:
    def test_get_generates_async_function(self):
        code = generate_classes(ep("GET", "/api/users"), "javascript")
        assert "async function getUsers" in code
        assert "method: 'GET'" in code
        assert "response.json()" in code
        assert "BASE_URL" in code

    def test_post_generates_create_with_body(self):
        code = generate_classes(ep("POST", "/api/users"), "javascript")
        assert "async function createUser" in code
        assert "method: 'POST'" in code
        assert "JSON.stringify" in code

    def test_put_generates_update_with_id(self):
        code = generate_classes(ep("PUT", "/api/users"), "javascript")
        assert "async function updateUser" in code
        assert "method: 'PUT'" in code

    def test_delete_generates_delete_with_id(self):
        code = generate_classes(ep("DELETE", "/api/users"), "javascript")
        assert "async function deleteUser" in code
        assert "method: 'DELETE'" in code

    def test_multiple_endpoints_all_present(self):
        endpoints = [
            {"method": "GET", "path": "/api/users"},
            {"method": "POST", "path": "/api/users"},
        ]
        code = generate_classes(endpoints, "javascript")
        assert "async function getUsers" in code
        assert "async function createUser" in code

    def test_unsupported_language_raises(self):
        with pytest.raises(ValueError, match="Unsupported language"):
            generate_classes(ep("GET", "/api/users"), "cobol")


class TestGenerateClassesTS:
    def test_get_has_promise_return_type(self):
        code = generate_classes(ep("GET", "/api/users"), "typescript")
        assert "Promise<void>" in code
        assert "async function getUsers" in code

    def test_get_has_typed_response(self):
        code = generate_classes(ep("GET", "/api/users"), "typescript")
        assert "unknown" in code or ": unknown" in code

    def test_post_has_body_and_stringify(self):
        code = generate_classes(ep("POST", "/api/users"), "typescript")
        assert "async function createUser" in code
        assert "JSON.stringify" in code

    def test_put_has_promise_return_type(self):
        code = generate_classes(ep("PUT", "/api/users"), "typescript")
        assert "Promise<void>" in code

    def test_delete_has_promise_return_type(self):
        code = generate_classes(ep("DELETE", "/api/users"), "typescript")
        assert "Promise<void>" in code


class TestGenerateClassesPython:
    def test_get_uses_requests(self):
        code = generate_classes(ep("GET", "/api/users"), "python")
        assert "import requests" in code
        assert "def get_users" in code
        assert "requests.get(" in code
        assert "raise_for_status()" in code

    def test_post_uses_requests_post(self):
        code = generate_classes(ep("POST", "/api/users"), "python")
        assert "def create_user" in code
        assert "requests.post(" in code

    def test_put_uses_requests_put(self):
        code = generate_classes(ep("PUT", "/api/users"), "python")
        assert "def update_user" in code
        assert "requests.put(" in code

    def test_delete_uses_requests_delete(self):
        code = generate_classes(ep("DELETE", "/api/users"), "python")
        assert "def delete_user" in code
        assert "requests.delete(" in code


class TestGenerateClassesCSharp:
    def test_get_uses_httpclient(self):
        code = generate_classes(ep("GET", "/api/users"), "csharp")
        assert "HttpClient" in code
        assert "GetAsync" in code
        assert "async Task" in code

    def test_post_uses_post_async(self):
        code = generate_classes(ep("POST", "/api/users"), "csharp")
        assert "PostAsync" in code or "PostAsJsonAsync" in code

    def test_put_uses_put_async(self):
        code = generate_classes(ep("PUT", "/api/users"), "csharp")
        assert "PutAsync" in code or "PutAsJsonAsync" in code

    def test_delete_uses_delete_async(self):
        code = generate_classes(ep("DELETE", "/api/users"), "csharp")
        assert "DeleteAsync" in code


class TestGenerateClassesJava:
    def test_get_uses_httpclient(self):
        code = generate_classes(ep("GET", "/api/users"), "java")
        assert "HttpClient" in code
        assert "HttpRequest" in code
        assert "getUsers" in code

    def test_post_sends_body(self):
        code = generate_classes(ep("POST", "/api/users"), "java")
        assert "createUser" in code
        assert "BodyPublishers" in code

    def test_put_uses_put_method(self):
        code = generate_classes(ep("PUT", "/api/users"), "java")
        assert "updateUser" in code
        assert "PUT" in code

    def test_delete_uses_delete_method(self):
        code = generate_classes(ep("DELETE", "/api/users"), "java")
        assert "deleteUser" in code
        assert "DELETE" in code
