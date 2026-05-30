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
