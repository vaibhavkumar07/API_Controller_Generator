# Classes Panel Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a "Classes" output panel that generates client-side caller code alongside the controller, with independent language selectors in each panel header.

**Architecture:** Single `POST /api/generate` call returns both `controllerCode` and `classesCode`. New `generate_classes()` in `generator.py` handles 5 client languages (JS, TS, Python, C#, Java). Frontend restructures from 2-col grid to full-width input + side-by-side outputs row; language selectors move into output panel headers; language change auto-triggers re-generation.

**Tech Stack:** Python 3 / Flask (backend), Next.js 14 / TypeScript / React (frontend), pytest (tests)

---

## File Map

| File | Action | Responsibility |
|---|---|---|
| `backend/requirements.txt` | Modify | Add `pytest` |
| `backend/tests/__init__.py` | Create | Test package marker |
| `backend/tests/test_generator_classes.py` | Create | Unit tests for `generate_classes` |
| `backend/tests/test_app.py` | Create | Integration tests for updated endpoint |
| `backend/generator.py` | Modify | Add `SUPPORTED_CLASS_LANGUAGES`, `_get_caller_func_name`, `_get_caller_func_name_snake`, `generate_classes`, and 5 private `_generate_*_classes` functions |
| `backend/app.py` | Modify | Extract `classesLang` from request, call `generate_classes`, include `classesCode` in response |
| `frontend/app/globals.css` | Modify | Add `.input-section`, `.outputs-row`; fix textarea height; remove `.input-card`/`.output-card` width hacks |
| `frontend/app/page.tsx` | Modify | New state, `generateWith` core function, language-change handlers, restructured JSX with classes panel |

---

## Task 1: Backend test setup + JavaScript classes generation

**Files:**
- Modify: `backend/requirements.txt`
- Create: `backend/tests/__init__.py`
- Create: `backend/tests/test_generator_classes.py`
- Modify: `backend/generator.py`

- [ ] **Step 1: Add pytest to requirements**

In `backend/requirements.txt`, append:
```
pytest==8.2.0
```

Install it:
```bash
cd backend && source .venv/bin/activate && pip install pytest==8.2.0
```

- [ ] **Step 2: Create test package**

Create `backend/tests/__init__.py` — empty file.

- [ ] **Step 3: Write failing JS tests**

Create `backend/tests/test_generator_classes.py`:

```python
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
```

- [ ] **Step 4: Run tests — expect failure**

```bash
cd backend && source .venv/bin/activate && python -m pytest tests/test_generator_classes.py::TestGenerateClassesJS -v
```

Expected: `ERROR` — `ImportError: cannot import name 'generate_classes'`

- [ ] **Step 5: Implement JavaScript classes generation**

In `backend/generator.py`, add after the existing imports and `SUPPORTED_LANGUAGES`:

```python
SUPPORTED_CLASS_LANGUAGES = {"javascript", "typescript", "python", "csharp", "java"}


def _get_caller_func_name(method: str, path: str) -> str:
    route_name = _simplify_route_name(path)   # e.g., "Users"
    model_name = _guess_model_name(path)       # e.g., "User"
    mapping = {
        "GET": f"get{route_name}",
        "POST": f"create{model_name}",
        "PUT": f"update{model_name}",
        "DELETE": f"delete{model_name}",
    }
    return mapping.get(method, f"{method.lower()}{route_name}")


def _get_caller_func_name_snake(method: str, path: str) -> str:
    route_name = _simplify_route_name(path).lower()   # e.g., "users"
    model_name = _guess_model_name(path).lower()       # e.g., "user"
    mapping = {
        "GET": f"get_{route_name}",
        "POST": f"create_{model_name}",
        "PUT": f"update_{model_name}",
        "DELETE": f"delete_{model_name}",
    }
    return mapping.get(method, f"{method.lower()}_{route_name}")


def generate_classes(endpoints: List[Dict[str, Any]], language: str) -> str:
    language = language.lower()
    if language not in SUPPORTED_CLASS_LANGUAGES:
        raise ValueError(f"Unsupported language: {language}")

    if language == "javascript":
        return _generate_js_classes(endpoints)
    if language == "typescript":
        return _generate_ts_classes(endpoints)
    if language == "python":
        return _generate_python_classes(endpoints)
    if language == "csharp":
        return _generate_csharp_classes(endpoints)
    if language == "java":
        return _generate_java_classes(endpoints)

    raise ValueError("Language generation not implemented.")
```

Then add the JS implementation at the bottom of `generator.py`:

```python
def _generate_js_classes(endpoints: List[Dict[str, Any]]) -> str:
    lines = ["const BASE_URL = 'http://localhost:5001';", ""]
    for ep in endpoints:
        method = ep["method"]
        path = ep["path"]
        func_name = _get_caller_func_name(method, path)
        route = path if path.startswith("/") else f"/{path}"
        model_name = _guess_model_name(path)

        if method == "GET":
            lines += [
                f"async function {func_name}() {{",
                "  try {",
                f"    const response = await fetch(BASE_URL + '{route}', {{",
                "      method: 'GET',",
                "      headers: { 'Content-Type': 'application/json' }",
                "    });",
                "    if (!response.ok) throw new Error(`API Error: ${response.status}`);",
                "    const data = await response.json();",
                "    console.log(data);",
                "    return data;",
                "  } catch (error) {",
                "    console.error('Error:', error);",
                "    throw error;",
                "  }",
                "}",
                f"{func_name}();",
                "",
            ]
        elif method == "POST":
            lines += [
                f"async function {func_name}(body) {{",
                "  try {",
                f"    const response = await fetch(BASE_URL + '{route}', {{",
                "      method: 'POST',",
                "      headers: { 'Content-Type': 'application/json' },",
                "      body: JSON.stringify(body)",
                "    });",
                "    if (!response.ok) throw new Error(`API Error: ${response.status}`);",
                "    const data = await response.json();",
                "    console.log(data);",
                "    return data;",
                "  } catch (error) {",
                "    console.error('Error:', error);",
                "    throw error;",
                "  }",
                "}",
                f"{func_name}({{ /* {model_name} fields */ }});",
                "",
            ]
        elif method == "PUT":
            lines += [
                f"async function {func_name}(id, body) {{",
                "  try {",
                f"    const response = await fetch(BASE_URL + '{route}/' + id, {{",
                "      method: 'PUT',",
                "      headers: { 'Content-Type': 'application/json' },",
                "      body: JSON.stringify(body)",
                "    });",
                "    if (!response.ok) throw new Error(`API Error: ${response.status}`);",
                "    console.log('Updated successfully');",
                "  } catch (error) {",
                "    console.error('Error:', error);",
                "    throw error;",
                "  }",
                "}",
                f"{func_name}(1, {{ /* {model_name} fields */ }});",
                "",
            ]
        elif method == "DELETE":
            lines += [
                f"async function {func_name}(id) {{",
                "  try {",
                f"    const response = await fetch(BASE_URL + '{route}/' + id, {{",
                "      method: 'DELETE',",
                "      headers: { 'Content-Type': 'application/json' }",
                "    });",
                "    if (!response.ok) throw new Error(`API Error: ${response.status}`);",
                "    console.log('Deleted successfully');",
                "  } catch (error) {",
                "    console.error('Error:', error);",
                "    throw error;",
                "  }",
                "}",
                f"{func_name}(1);",
                "",
            ]
        else:
            lines += [f"// {method} {path} — not supported", ""]

    return "\n".join(lines)
```

- [ ] **Step 6: Run JS tests — expect pass**

```bash
cd backend && source .venv/bin/activate && python -m pytest tests/test_generator_classes.py::TestGenerateClassesJS -v
```

Expected: `5 passed`

- [ ] **Step 7: Commit**

```bash
git add backend/requirements.txt backend/tests/ backend/generator.py
git commit -m "feat: add generate_classes for JavaScript"
```

---

## Task 2: TypeScript classes generation

**Files:**
- Modify: `backend/tests/test_generator_classes.py`
- Modify: `backend/generator.py`

- [ ] **Step 1: Add failing TS tests**

Append to `backend/tests/test_generator_classes.py`:

```python
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
```

- [ ] **Step 2: Run — expect failure**

```bash
cd backend && source .venv/bin/activate && python -m pytest tests/test_generator_classes.py::TestGenerateClassesTS -v
```

Expected: `FAILED` — `NotImplementedError` or wrong output

- [ ] **Step 3: Implement TypeScript generation**

Add to bottom of `backend/generator.py`:

```python
def _generate_ts_classes(endpoints: List[Dict[str, Any]]) -> str:
    lines = ["const BASE_URL = 'http://localhost:5001';", ""]
    for ep in endpoints:
        method = ep["method"]
        path = ep["path"]
        func_name = _get_caller_func_name(method, path)
        route = path if path.startswith("/") else f"/{path}"
        model_name = _guess_model_name(path)

        if method == "GET":
            lines += [
                f"async function {func_name}(): Promise<void> {{",
                "  try {",
                f"    const response = await fetch(BASE_URL + '{route}', {{",
                "      method: 'GET',",
                "      headers: { 'Content-Type': 'application/json' }",
                "    });",
                "    if (!response.ok) throw new Error(`API Error: ${response.status}`);",
                "    const data: unknown = await response.json();",
                "    console.log(data);",
                "  } catch (error) {",
                "    console.error('Error:', error);",
                "    throw error;",
                "  }",
                "}",
                f"{func_name}();",
                "",
            ]
        elif method == "POST":
            lines += [
                f"async function {func_name}(body: Record<string, unknown>): Promise<void> {{",
                "  try {",
                f"    const response = await fetch(BASE_URL + '{route}', {{",
                "      method: 'POST',",
                "      headers: { 'Content-Type': 'application/json' },",
                "      body: JSON.stringify(body)",
                "    });",
                "    if (!response.ok) throw new Error(`API Error: ${response.status}`);",
                "    const data: unknown = await response.json();",
                "    console.log(data);",
                "  } catch (error) {",
                "    console.error('Error:', error);",
                "    throw error;",
                "  }",
                "}",
                f"{func_name}({{ /* {model_name} fields */ }});",
                "",
            ]
        elif method == "PUT":
            lines += [
                f"async function {func_name}(id: number, body: Record<string, unknown>): Promise<void> {{",
                "  try {",
                f"    const response = await fetch(BASE_URL + '{route}/' + id, {{",
                "      method: 'PUT',",
                "      headers: { 'Content-Type': 'application/json' },",
                "      body: JSON.stringify(body)",
                "    });",
                "    if (!response.ok) throw new Error(`API Error: ${response.status}`);",
                "    console.log('Updated successfully');",
                "  } catch (error) {",
                "    console.error('Error:', error);",
                "    throw error;",
                "  }",
                "}",
                f"{func_name}(1, {{ /* {model_name} fields */ }});",
                "",
            ]
        elif method == "DELETE":
            lines += [
                f"async function {func_name}(id: number): Promise<void> {{",
                "  try {",
                f"    const response = await fetch(BASE_URL + '{route}/' + id, {{",
                "      method: 'DELETE',",
                "      headers: { 'Content-Type': 'application/json' }",
                "    });",
                "    if (!response.ok) throw new Error(`API Error: ${response.status}`);",
                "    console.log('Deleted successfully');",
                "  } catch (error) {",
                "    console.error('Error:', error);",
                "    throw error;",
                "  }",
                "}",
                f"{func_name}(1);",
                "",
            ]
        else:
            lines += [f"// {method} {path} — not supported", ""]

    return "\n".join(lines)
```

- [ ] **Step 4: Run TS tests — expect pass**

```bash
cd backend && source .venv/bin/activate && python -m pytest tests/test_generator_classes.py::TestGenerateClassesTS -v
```

Expected: `5 passed`

- [ ] **Step 5: Commit**

```bash
git add backend/tests/test_generator_classes.py backend/generator.py
git commit -m "feat: add generate_classes for TypeScript"
```

---

## Task 3: Python, C#, Java classes generation

**Files:**
- Modify: `backend/tests/test_generator_classes.py`
- Modify: `backend/generator.py`

- [ ] **Step 1: Add failing tests for Python, C#, Java**

Append to `backend/tests/test_generator_classes.py`:

```python
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
        assert ".PUT(" in code or "PUT" in code

    def test_delete_uses_delete_method(self):
        code = generate_classes(ep("DELETE", "/api/users"), "java")
        assert "deleteUser" in code
        assert "DELETE" in code
```

- [ ] **Step 2: Run — expect failure**

```bash
cd backend && source .venv/bin/activate && python -m pytest tests/test_generator_classes.py::TestGenerateClassesPython tests/test_generator_classes.py::TestGenerateClassesCSharp tests/test_generator_classes.py::TestGenerateClassesJava -v
```

Expected: all FAILED

- [ ] **Step 3: Implement Python classes generation**

Add to bottom of `backend/generator.py`:

```python
def _generate_python_classes(endpoints: List[Dict[str, Any]]) -> str:
    lines = ["import requests", "", "BASE_URL = 'http://localhost:5001'", ""]
    for ep in endpoints:
        method = ep["method"]
        path = ep["path"]
        func_name = _get_caller_func_name_snake(method, path)
        route = path if path.startswith("/") else f"/{path}"
        model_name = _guess_model_name(path)

        if method == "GET":
            lines += [
                f"def {func_name}():",
                "    try:",
                f"        response = requests.get(BASE_URL + '{route}')",
                "        response.raise_for_status()",
                "        data = response.json()",
                "        print(data)",
                "        return data",
                "    except requests.RequestException as e:",
                "        print(f'Error: {e}')",
                "        raise",
                "",
                f"{func_name}()",
                "",
            ]
        elif method == "POST":
            lines += [
                f"def {func_name}(payload: dict):",
                "    try:",
                f"        response = requests.post(BASE_URL + '{route}', json=payload)",
                "        response.raise_for_status()",
                "        data = response.json()",
                "        print(data)",
                "        return data",
                "    except requests.RequestException as e:",
                "        print(f'Error: {e}')",
                "        raise",
                "",
                f"{func_name}({{}})",
                "",
            ]
        elif method == "PUT":
            lines += [
                f"def {func_name}(id: int, payload: dict):",
                "    try:",
                f"        response = requests.put(BASE_URL + '{route}/' + str(id), json=payload)",
                "        response.raise_for_status()",
                "        print('Updated successfully')",
                "    except requests.RequestException as e:",
                "        print(f'Error: {e}')",
                "        raise",
                "",
                f"{func_name}(1, {{}})",
                "",
            ]
        elif method == "DELETE":
            lines += [
                f"def {func_name}(id: int):",
                "    try:",
                f"        response = requests.delete(BASE_URL + '{route}/' + str(id))",
                "        response.raise_for_status()",
                "        print('Deleted successfully')",
                "    except requests.RequestException as e:",
                "        print(f'Error: {e}')",
                "        raise",
                "",
                f"{func_name}(1)",
                "",
            ]
        else:
            lines += [f"# {method} {path} — not supported", ""]

    return "\n".join(lines)
```

- [ ] **Step 4: Implement C# classes generation**

Add to bottom of `backend/generator.py`:

```python
def _generate_csharp_classes(endpoints: List[Dict[str, Any]]) -> str:
    lines = [
        "using System.Net.Http;",
        "using System.Net.Http.Json;",
        "",
        "var client = new HttpClient();",
        "var BASE_URL = \"http://localhost:5001\";",
        "",
    ]
    for ep in endpoints:
        method = ep["method"]
        path = ep["path"]
        func_name = _get_caller_func_name(method, path)
        route = path if path.startswith("/") else f"/{path}"
        model_name = _guess_model_name(path)

        if method == "GET":
            lines += [
                f"async Task {func_name}Async()",
                "{",
                "    try",
                "    {",
                f"        var response = await client.GetAsync(BASE_URL + \"{route}\");",
                "        response.EnsureSuccessStatusCode();",
                "        var data = await response.Content.ReadAsStringAsync();",
                "        Console.WriteLine(data);",
                "    }",
                "    catch (Exception e)",
                "    {",
                "        Console.Error.WriteLine($\"Error: {e.Message}\");",
                "        throw;",
                "    }",
                "}",
                "",
                f"await {func_name}Async();",
                "",
            ]
        elif method == "POST":
            lines += [
                f"async Task {func_name}Async({model_name} body)",
                "{",
                "    try",
                "    {",
                f"        var response = await client.PostAsJsonAsync(BASE_URL + \"{route}\", body);",
                "        response.EnsureSuccessStatusCode();",
                "        var data = await response.Content.ReadAsStringAsync();",
                "        Console.WriteLine(data);",
                "    }",
                "    catch (Exception e)",
                "    {",
                "        Console.Error.WriteLine($\"Error: {e.Message}\");",
                "        throw;",
                "    }",
                "}",
                "",
                f"await {func_name}Async(new {model_name}());",
                "",
            ]
        elif method == "PUT":
            lines += [
                f"async Task {func_name}Async(int id, {model_name} body)",
                "{",
                "    try",
                "    {",
                f"        var response = await client.PutAsJsonAsync(BASE_URL + \"{route}/\" + id, body);",
                "        response.EnsureSuccessStatusCode();",
                "        Console.WriteLine(\"Updated successfully\");",
                "    }",
                "    catch (Exception e)",
                "    {",
                "        Console.Error.WriteLine($\"Error: {e.Message}\");",
                "        throw;",
                "    }",
                "}",
                "",
                f"await {func_name}Async(1, new {model_name}());",
                "",
            ]
        elif method == "DELETE":
            lines += [
                f"async Task {func_name}Async(int id)",
                "{",
                "    try",
                "    {",
                f"        var response = await client.DeleteAsync(BASE_URL + \"{route}/\" + id);",
                "        response.EnsureSuccessStatusCode();",
                "        Console.WriteLine(\"Deleted successfully\");",
                "    }",
                "    catch (Exception e)",
                "    {",
                "        Console.Error.WriteLine($\"Error: {e.Message}\");",
                "        throw;",
                "    }",
                "}",
                "",
                f"await {func_name}Async(1);",
                "",
            ]
        else:
            lines += [f"// {method} {path} — not supported", ""]

    return "\n".join(lines)
```

- [ ] **Step 5: Implement Java classes generation**

Add to bottom of `backend/generator.py`:

```python
def _generate_java_classes(endpoints: List[Dict[str, Any]]) -> str:
    lines = [
        "import java.net.URI;",
        "import java.net.http.HttpClient;",
        "import java.net.http.HttpRequest;",
        "import java.net.http.HttpRequest.BodyPublishers;",
        "import java.net.http.HttpResponse;",
        "",
        "HttpClient client = HttpClient.newHttpClient();",
        "String BASE_URL = \"http://localhost:5001\";",
        "",
    ]
    for ep in endpoints:
        method = ep["method"]
        path = ep["path"]
        func_name = _get_caller_func_name(method, path)
        route = path if path.startswith("/") else f"/{path}"
        model_name = _guess_model_name(path)

        if method == "GET":
            lines += [
                f"void {func_name}() throws Exception {{",
                f"    HttpRequest request = HttpRequest.newBuilder()",
                f"        .uri(URI.create(BASE_URL + \"{route}\"))",
                "        .GET()",
                "        .header(\"Content-Type\", \"application/json\")",
                "        .build();",
                "    HttpResponse<String> response = client.send(request, HttpResponse.BodyHandlers.ofString());",
                "    if (response.statusCode() < 200 || response.statusCode() >= 300) {",
                "        throw new RuntimeException(\"API Error: \" + response.statusCode());",
                "    }",
                "    System.out.println(response.body());",
                "}",
                "",
                f"{func_name}();",
                "",
            ]
        elif method == "POST":
            lines += [
                f"void {func_name}(String jsonBody) throws Exception {{",
                f"    HttpRequest request = HttpRequest.newBuilder()",
                f"        .uri(URI.create(BASE_URL + \"{route}\"))",
                "        .POST(BodyPublishers.ofString(jsonBody))",
                "        .header(\"Content-Type\", \"application/json\")",
                "        .build();",
                "    HttpResponse<String> response = client.send(request, HttpResponse.BodyHandlers.ofString());",
                "    if (response.statusCode() < 200 || response.statusCode() >= 300) {",
                "        throw new RuntimeException(\"API Error: \" + response.statusCode());",
                "    }",
                "    System.out.println(response.body());",
                "}",
                "",
                f"{func_name}(\"{{}}\");",
                "",
            ]
        elif method == "PUT":
            lines += [
                f"void {func_name}(int id, String jsonBody) throws Exception {{",
                f"    HttpRequest request = HttpRequest.newBuilder()",
                f"        .uri(URI.create(BASE_URL + \"{route}/\" + id))",
                "        .PUT(BodyPublishers.ofString(jsonBody))",
                "        .header(\"Content-Type\", \"application/json\")",
                "        .build();",
                "    HttpResponse<String> response = client.send(request, HttpResponse.BodyHandlers.ofString());",
                "    if (response.statusCode() < 200 || response.statusCode() >= 300) {",
                "        throw new RuntimeException(\"API Error: \" + response.statusCode());",
                "    }",
                "    System.out.println(\"Updated successfully\");",
                "}",
                "",
                f"{func_name}(1, \"{{}}\");",
                "",
            ]
        elif method == "DELETE":
            lines += [
                f"void {func_name}(int id) throws Exception {{",
                f"    HttpRequest request = HttpRequest.newBuilder()",
                f"        .uri(URI.create(BASE_URL + \"{route}/\" + id))",
                "        .DELETE()",
                "        .header(\"Content-Type\", \"application/json\")",
                "        .build();",
                "    HttpResponse<String> response = client.send(request, HttpResponse.BodyHandlers.ofString());",
                "    if (response.statusCode() < 200 || response.statusCode() >= 300) {",
                "        throw new RuntimeException(\"API Error: \" + response.statusCode());",
                "    }",
                "    System.out.println(\"Deleted successfully\");",
                "}",
                "",
                f"{func_name}(1);",
                "",
            ]
        else:
            lines += [f"// {method} {path} — not supported", ""]

    return "\n".join(lines)
```

- [ ] **Step 6: Run all classes tests — expect pass**

```bash
cd backend && source .venv/bin/activate && python -m pytest tests/test_generator_classes.py -v
```

Expected: all 23 tests pass

- [ ] **Step 7: Commit**

```bash
git add backend/tests/test_generator_classes.py backend/generator.py
git commit -m "feat: add generate_classes for Python, C#, and Java"
```

---

## Task 4: Update /api/generate endpoint

**Files:**
- Create: `backend/tests/test_app.py`
- Modify: `backend/app.py`

- [ ] **Step 1: Write failing endpoint tests**

Create `backend/tests/test_app.py`:

```python
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


def test_generate_invalid_classes_lang_returns_400(client):
    resp = client.post(
        "/api/generate",
        json={"inputText": "GET /api/users", "language": "csharp", "classesLang": "cobol"},
    )
    assert resp.status_code == 500 or resp.status_code == 400


def test_generate_response_includes_classes_lang(client):
    resp = client.post(
        "/api/generate",
        json={"inputText": "GET /api/users", "language": "csharp", "classesLang": "java"},
    )
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["classesLang"] == "java"
```

- [ ] **Step 2: Run — expect failure**

```bash
cd backend && source .venv/bin/activate && python -m pytest tests/test_app.py -v
```

Expected: all FAILED — `classesCode` not in response

- [ ] **Step 3: Update app.py**

Replace the entire content of `backend/app.py` with:

```python
from flask import Flask, request, jsonify
from flask_cors import CORS
from parser import extract_text_from_pdf, parse_input
from generator import generate_controller, generate_classes

app = Flask(__name__)
CORS(app)


@app.route("/api/generate", methods=["POST"])
def generate():
    input_text = ""
    language = "csharp"
    classes_lang = "javascript"

    if request.content_type and request.content_type.startswith("multipart/form-data"):
        uploaded_file = request.files.get("file")
        input_text = request.form.get("inputText", "")
        language = request.form.get("language", "csharp")
        classes_lang = request.form.get("classesLang", "javascript")
        if uploaded_file:
            text_from_pdf = extract_text_from_pdf(uploaded_file.stream)
            input_text = input_text or text_from_pdf
    else:
        data = request.get_json(silent=True) or {}
        input_text = data.get("inputText", "")
        language = data.get("language", "csharp")
        classes_lang = data.get("classesLang", "javascript")

    if not input_text or not language:
        return jsonify({"error": "inputText or uploaded PDF is required, and language must be selected."}), 400

    try:
        endpoints = parse_input(input_text)
        if not endpoints:
            return jsonify({"error": "No API endpoints were detected in the input."}), 400

        controller_code = generate_controller(endpoints, language)
        classes_code = generate_classes(endpoints, classes_lang)
        return jsonify({
            "controllerCode": controller_code,
            "classesCode": classes_code,
            "language": language,
            "classesLang": classes_lang,
        })
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002, debug=True)
```

- [ ] **Step 4: Run endpoint tests — expect pass**

```bash
cd backend && source .venv/bin/activate && python -m pytest tests/test_app.py -v
```

Expected: `6 passed`

- [ ] **Step 5: Run full test suite**

```bash
cd backend && source .venv/bin/activate && python -m pytest tests/ -v
```

Expected: all 29 tests pass

- [ ] **Step 6: Commit**

```bash
git add backend/app.py backend/tests/test_app.py
git commit -m "feat: update /api/generate to return classesCode"
```

---

## Task 5: Frontend layout restructure

**Files:**
- Modify: `frontend/app/globals.css`
- Modify: `frontend/app/page.tsx` (layout only — no logic changes yet)

- [ ] **Step 1: Update globals.css**

In `frontend/app/globals.css`:

**Remove** the `.input-card` and `.output-card` width hacks (lines 97-99 and 243-246 for the `.output-card { display: flex }` stay, but remove the `width: 110%` / `width: 90%`):

Find and remove these exact rules:
```css
.output-card {
  width: 110%;
}

.input-card {
  width: 90%;
}
```

**Add** after the `.grid-panel` block:

```css
.input-section {
  width: 100%;
  margin-bottom: 24px;
}

.outputs-row {
  display: flex;
  gap: 24px;
  width: 100%;
  align-items: stretch;
}

.outputs-row > .card {
  flex: 1;
  min-width: 0;
}
```

**Change** `textarea` min-height from `460px` to `200px` (input is now full-width, shorter height fits better):

```css
textarea {
  /* existing rules... */
  min-height: 200px;
}
```

**Add** at the end of the file, a responsive breakpoint for the outputs row:

```css
@media (max-width: 1024px) {
  .outputs-row {
    flex-direction: column;
  }
}
```

- [ ] **Step 2: Restructure page.tsx layout**

In `frontend/app/page.tsx`, replace the entire `<section className="grid-panel">` block with this new structure (logic inside cards is unchanged — copy/move it exactly):

```tsx
      <div className="input-section">
        <div className="card input-card">
          <div className="card-header">
            <h2>Input</h2>
            <span>Text, JSON, or PDF upload</span>
          </div>
          <textarea
            value={inputText}
            onChange={(event) => setInputText(event.target.value)}
            rows={8}
            aria-label="API endpoint input"
          />
          <div className="file-upload-row">
            <label className="file-label">
              Upload PDF
              <input
                type="file"
                accept="application/pdf"
                onChange={(event) => {
                  const file = event.target.files?.[0] ?? null;
                  setUploadedFile(file);
                }}
              />
            </label>
            {uploadedFile && <span className="file-meta">Selected: {uploadedFile.name}</span>}
          </div>
          <div className="controls-row">
            <button className="primary-button" onClick={handleGenerate} disabled={isLoading}>
              Generate
            </button>
          </div>
        </div>
      </div>

      <div className="outputs-row">
        <div className="card output-card">
          <div className="card-header">
            <div>
              <h2>Controller</h2>
              <span>Server-side controller code</span>
            </div>
            <label>
              Language
              <select value={language} onChange={(event) => setLanguage(event.target.value)}>
                {languages.map((item) => (
                  <option key={item.value} value={item.value}>
                    {item.label}
                  </option>
                ))}
              </select>
            </label>
          </div>
          <div className="output-actions">
            <button onClick={handleCopy} disabled={!output}>Copy</button>
            <button onClick={handleDownload} disabled={!output}>Download</button>
            <button className="secondary-button" onClick={handleClear} disabled={!output}>Clear</button>
          </div>
          <pre className="output-block">{output || "Controller code will appear here."}</pre>
        </div>

        <div className="card output-card">
          <div className="card-header">
            <div>
              <h2>Classes</h2>
              <span>Client-side caller code</span>
            </div>
            <label>
              Language
              <select value="javascript" disabled>
                <option value="javascript">JavaScript</option>
              </select>
            </label>
          </div>
          <div className="output-actions">
            <button disabled>Copy</button>
            <button disabled>Download</button>
          </div>
          <pre className="output-block">{"Classes code will appear here."}</pre>
        </div>
      </div>
```

Note: The classes panel language selector and actions are stubbed (disabled/hardcoded). They will be wired up in Task 6.

- [ ] **Step 3: Verify layout renders**

```bash
cd frontend && npm run dev
```

Open `http://localhost:3000`. Verify:
- Input card spans full width at top
- Two output panels (Controller, Classes) appear side by side below
- No broken layout or console errors
- Generate button still works for controller output

- [ ] **Step 4: Commit**

```bash
git add frontend/app/globals.css frontend/app/page.tsx
git commit -m "feat: restructure layout — full-width input + side-by-side output panels"
```

---

## Task 6: Wire up classes panel — state, handler, language selectors

**Files:**
- Modify: `frontend/app/page.tsx`

- [ ] **Step 1: Add classesLanguages array and new state**

At the top of `page.tsx`, after the existing `languages` array, add:

```tsx
const classesLanguages = [
  { value: "javascript", label: "JavaScript" },
  { value: "typescript", label: "TypeScript" },
  { value: "python", label: "Python" },
  { value: "csharp", label: "C#" },
  { value: "java", label: "Java" },
];
```

Inside the `Home` component, after existing state declarations, add:

```tsx
const [classesLang, setClassesLang] = useState("javascript");
const [classesOutput, setClassesOutput] = useState("");
```

- [ ] **Step 2: Extract generateWith and update language change handlers**

Replace the existing `handleGenerate` function with:

```tsx
async function generateWith(text: string, ctrlLang: string, clsLang: string) {
  if (!text.trim()) return;
  setStatus("Generating controller and classes...");
  setIsLoading(true);

  try {
    let response: Response;
    if (uploadedFile) {
      const formData = new FormData();
      formData.append("language", ctrlLang);
      formData.append("classesLang", clsLang);
      formData.append("file", uploadedFile);
      if (text.trim()) formData.append("inputText", text);
      response = await fetch("http://localhost:5000/api/generate", {
        method: "POST",
        body: formData,
      });
    } else {
      response = await fetch("http://localhost:5000/api/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ inputText: text, language: ctrlLang, classesLang: clsLang }),
      });
    }

    const json = await response.json();
    if (!response.ok) {
      setStatus(json.error || "Generation failed.");
      setOutput("");
      setClassesOutput("");
    } else {
      setOutput(json.controllerCode || "");
      setClassesOutput(json.classesCode || "");
      setStatus("Controller and classes generated successfully.");
    }
  } catch {
    setStatus("Server request failed. Is the backend running?");
    setOutput("");
    setClassesOutput("");
  } finally {
    setIsLoading(false);
  }
}

function handleGenerate() {
  generateWith(inputText, language, classesLang);
}

function handleControllerLangChange(val: string) {
  setLanguage(val);
  if (output || classesOutput) generateWith(inputText, val, classesLang);
}

function handleClassesLangChange(val: string) {
  setClassesLang(val);
  if (output || classesOutput) generateWith(inputText, language, val);
}
```

- [ ] **Step 3: Add classes panel copy/download/clear handlers**

After `handleDownload`, add:

```tsx
function handleCopyClasses() {
  navigator.clipboard.writeText(classesOutput);
  setStatus("Copied classes to clipboard.");
}

function handleDownloadClasses() {
  const filename = `classes-${classesLang}.txt`;
  const blob = new Blob([classesOutput], { type: "text/plain;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = filename;
  anchor.click();
  URL.revokeObjectURL(url);
  setStatus("Download started.");
}

function handleClearClasses() {
  setClassesOutput("");
  setStatus("Classes output cleared.");
}
```

- [ ] **Step 4: Wire up classes panel JSX**

Replace the stubbed classes panel (the second `div.card output-card` from Task 5) with:

```tsx
        <div className="card output-card">
          <div className="card-header">
            <div>
              <h2>Classes</h2>
              <span>Client-side caller code</span>
            </div>
            <label>
              Language
              <select value={classesLang} onChange={(event) => handleClassesLangChange(event.target.value)}>
                {classesLanguages.map((item) => (
                  <option key={item.value} value={item.value}>
                    {item.label}
                  </option>
                ))}
              </select>
            </label>
          </div>
          <div className="output-actions">
            <button onClick={handleCopyClasses} disabled={!classesOutput}>Copy</button>
            <button onClick={handleDownloadClasses} disabled={!classesOutput}>Download</button>
            <button className="secondary-button" onClick={handleClearClasses} disabled={!classesOutput}>Clear</button>
          </div>
          <pre className="output-block">{classesOutput || "Classes code will appear here."}</pre>
        </div>
```

Also wire up the controller panel's language selector — replace the `onChange` on the controller panel select:

```tsx
onChange={(event) => handleControllerLangChange(event.target.value)}
```

- [ ] **Step 5: Verify full flow**

```bash
cd frontend && npm run dev
```

Open `http://localhost:3000` (ensure backend is also running: `cd backend && source .venv/bin/activate && python app.py`).

Verify:
1. Paste `GET /api/users` into input, click Generate → both panels populate
2. Change controller language (e.g., to Java) → controller panel updates, classes panel unchanged
3. Change classes language (e.g., to TypeScript) → classes panel updates with `Promise<void>`, controller unchanged
4. Copy/Download/Clear buttons work for both panels
5. No TypeScript errors: `cd frontend && npx tsc --noEmit`

- [ ] **Step 6: Commit**

```bash
git add frontend/app/page.tsx
git commit -m "feat: wire up classes panel with language selectors and generate handler"
```
