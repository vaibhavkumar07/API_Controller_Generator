import json
import re
from io import BytesIO
from typing import List, Dict, Any
from pypdf import PdfReader

ENDPOINT_PATTERN = re.compile(
    r"^(GET|POST|PUT|PATCH|DELETE|OPTIONS|HEAD)\s+([^\s]+)", re.IGNORECASE
)


def extract_text_from_pdf(file_obj: BytesIO) -> str:
    reader = PdfReader(file_obj)
    pages = [page.extract_text() or "" for page in reader.pages]
    return "\n".join(pages)


def _extract_json_payload(text: str) -> Any:
    stripped = text.strip()
    if not stripped:
        return None

    try:
        return json.loads(stripped)
    except json.JSONDecodeError:
        return None


def parse_input(raw_input: str) -> List[Dict[str, Any]]:
    lines = raw_input.strip().splitlines()
    endpoints = []
    current = None
    buffer = []

    for line in lines + [""]:
        match = ENDPOINT_PATTERN.match(line)
        if match:
            if current:
                endpoints.append(_build_endpoint(current, buffer))
                buffer = []
            current = {"method": match.group(1).upper(), "path": match.group(2), "response": None, "body": None}
            continue

        buffer.append(line)

    if current:
        endpoints.append(_build_endpoint(current, buffer))

    if not endpoints:
        json_payload = _extract_json_payload(raw_input)
        if isinstance(json_payload, list):
            return [{"method": "GET", "path": "/api/unknown", "response": json_payload, "body": None}]
        else:
            raise ValueError("No valid endpoint definitions found in the provided input.")

    return endpoints


def _build_endpoint(base: Dict[str, Any], lines: List[str]) -> Dict[str, Any]:
    data = base.copy()
    content = "\n".join(lines).strip()
    if not content:
        return data

    response_match = re.search(r"Response:\s*(.*)$", content, re.IGNORECASE | re.DOTALL)
    request_match = re.search(r"Request:\s*(.*)$", content, re.IGNORECASE | re.DOTALL)

    response_text = content
    if response_match:
        response_text = response_match.group(1).strip()
    elif request_match:
        response_text = content[:request_match.start()].strip()

    response_data = _extract_json_payload(response_text)
    if response_data is not None:
        data["response"] = response_data

    if request_match:
        request_text = request_match.group(1).strip()
        request_data = _extract_json_payload(request_text)
        if request_data is not None:
            data["body"] = request_data

    return data
