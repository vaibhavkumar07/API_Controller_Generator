from typing import List, Dict, Any


SUPPORTED_LANGUAGES = {"csharp", "java", "python"}
SUPPORTED_CLASS_LANGUAGES = {"javascript", "typescript", "python", "csharp", "java"}


def _to_pascal_case(value: str) -> str:
    return "".join(word.capitalize() for word in value.replace("/", " ").split())


def _simplify_route_name(path: str) -> str:
    trimmed = path.strip("/") or "root"
    return trimmed.split("/")[-1].capitalize()


def _guess_model_name(path: str) -> str:
    name = _simplify_route_name(path).lower()
    if name.endswith("es"):
        if len(name) > 2 and name[-3] == 'z':
            name = name[:-3]
        else:
            name = name[:-2]
    elif name.endswith("s"):
        name = name[:-1]
    return name.capitalize()


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
    # Used by _generate_python_classes
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
    raise ValueError(f"Language dispatch missing for: {language}")


def generate_controller(endpoints: List[Dict[str, Any]], language: str) -> str:
    language = language.lower()
    if language not in SUPPORTED_LANGUAGES:
        raise ValueError(f"Unsupported language: {language}")

    if language == "csharp":
        return _generate_csharp(endpoints)
    if language == "java":
        return _generate_java(endpoints)
    if language == "python":
        return _generate_python(endpoints)

    raise ValueError(f"Language dispatch missing for: {language}")


def _generate_csharp(endpoints: List[Dict[str, Any]]) -> str:
    controller_name = _simplify_route_name(endpoints[0]["path"]) + "Controller"
    lines = [f"[Route(\"api/[controller]\")]", f"public class {controller_name} : ControllerBase", "{", "    private readonly AppDbContext _context;", "", f"    public {controller_name}(AppDbContext context)", "    {", "        _context = context;", "    }", ""]

    for ep in endpoints:
        method = ep["method"]
        model_name = _guess_model_name(ep["path"])
        if method == "GET":
            lines += ["    [HttpGet]", "    public async Task<IActionResult> GetAll()", "    {", f"        return Ok(await _context.{_simplify_route_name(ep['path'])}.ToListAsync());", "    }", ""]
        elif method == "POST":
            lines += ["    [HttpPost]", f"    public async Task<IActionResult> Create({model_name} model)", "    {", f"        _context.{_simplify_route_name(ep['path'])}.Add(model);", "        await _context.SaveChangesAsync();", "        return Ok(model);", "    }", ""]
        elif method == "PUT":
            lines += [f"    [HttpPut(\"{{id}}\")]", f"    public async Task<IActionResult> Update(int id, {model_name} model)", "    {", "        if (id != model.Id) return BadRequest();", f"        _context.Entry(model).State = EntityState.Modified;", "        await _context.SaveChangesAsync();", "        return NoContent();", "    }", ""]
        elif method == "DELETE":
            lines += [f"    [HttpDelete(\"{{id}}\")]", "    public async Task<IActionResult> Delete(int id)", "    {", f"        var model = await _context.{_simplify_route_name(ep['path'])}.FindAsync(id);", "        if (model == null) return NotFound();", f"        _context.{_simplify_route_name(ep['path'])}.Remove(model);", "        await _context.SaveChangesAsync();", "        return NoContent();", "    }", ""]
        else:
            lines += [f"    [Http{method.title()}]", "    public IActionResult Unsupported()", "    {", "        return StatusCode(501);", "    }", ""]

    lines.append("}")
    return "\n".join(lines)


def _generate_java(endpoints: List[Dict[str, Any]]) -> str:
    class_name = _to_pascal_case(endpoints[0]["path"].strip("/")) or "Api"
    class_name = f"{class_name}Controller"
    lines = ["@RestController", "@RequestMapping(\"/api\")", f"public class {class_name} {{", "    private final AppService appService;", "", f"    public {class_name}(AppService appService) {{", "        this.appService = appService;", "    }", ""]

    for ep in endpoints:
        method = ep["method"]
        simple_name = ep["path"].strip("/").replace("/", "_") or "root"
        model_name = _guess_model_name(ep["path"])
        if method == "GET":
            lines += [f"    @GetMapping(\"/{ep['path'].strip('/') or ''}\")", f"    public ResponseEntity<List<{model_name}>> getAll{_to_pascal_case(simple_name)}() {{", "        return ResponseEntity.ok(appService.getAll());", "    }", ""]
        elif method == "POST":
            lines += [f"    @PostMapping(\"/{ep['path'].strip('/') or ''}\")", f"    public ResponseEntity<{model_name}> create{_to_pascal_case(simple_name)}(@RequestBody {model_name} request) {{", "        return ResponseEntity.ok(appService.create(request));", "    }", ""]
        elif method == "PUT":
            lines += [f"    @PutMapping(\"/{ep['path'].strip('/') or ''}/{{id}}\")", f"    public ResponseEntity<Void> update{_to_pascal_case(simple_name)}(@PathVariable Long id, @RequestBody {model_name} request) {{", "        appService.update(id, request);", "        return ResponseEntity.noContent().build();", "    }", ""]
        elif method == "DELETE":
            lines += [f"    @DeleteMapping(\"/{ep['path'].strip('/') or ''}/{{id}}\")", f"    public ResponseEntity<Void> delete{_to_pascal_case(simple_name)}(@PathVariable Long id) {{", "        appService.delete(id);", "        return ResponseEntity.noContent().build();", "    }", ""]
        else:
            lines += [f"    @RequestMapping(value = \"/{ep['path'].strip('/') or ''}\", method = RequestMethod.{method})", "    public ResponseEntity<Void> unsupported() {", "        return ResponseEntity.status(HttpStatus.NOT_IMPLEMENTED).build();", "    }", ""]

    lines.append("}")
    return "\n".join(lines)


def _generate_python(endpoints: List[Dict[str, Any]]) -> str:
    lines = ["from flask import Blueprint, request, jsonify", "", "api = Blueprint('api', __name__)", ""]
    for ep in endpoints:
        method = ep["method"]
        path = ep["path"]
        flask_path = path.replace("{", "<").replace("}", ">")
        func_name = _to_pascal_case(path.replace("/", "_"))
        model_name = _guess_model_name(ep["path"])
        lines += [f"@api.route('{flask_path}', methods=['{method}'])", f"def {func_name.lower()}():"]
        if method == "GET":
            lines += ["    # TODO: load all items from database", "    return jsonify([])", ""]
        elif method == "POST":
            lines += ["    payload = request.get_json()", "    # TODO: create new item using payload", "    return jsonify(payload), 201", ""]
        elif method == "PUT":
            lines += ["    payload = request.get_json()", "    # TODO: update existing item", "    return '', 204", ""]
        elif method == "DELETE":
            lines += ["    # TODO: delete an item", "    return '', 204", ""]
        else:
            lines += ["    return '', 501", ""]

    return "\n".join(lines)


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


def _generate_python_classes(endpoints: List[Dict[str, Any]]) -> str:
    # Used by generate_classes dispatch
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
