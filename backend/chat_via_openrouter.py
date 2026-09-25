import json

import requests

import config


REPORT_SCHEMA = {
    "type": "object",
    "properties": {
        "overall_status": {
            "type": "string",
            "enum": ["Normal", "Abnormal", "Requires Attention"],
        },
        "confidence": {"type": "number", "minimum": 0, "maximum": 100},
        "findings": {
            "type": "array",
            "minItems": 1,
            "maxItems": 1,
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "region": {"type": "string"},
                    "severity": {
                        "type": "string",
                        "enum": ["Normal", "Mild", "Moderate", "Severe"],
                    },
                    "confidence": {"type": "number", "minimum": 0, "maximum": 100},
                    "description": {"type": "string"},
                },
                "required": ["name", "region", "severity", "confidence", "description"],
                "additionalProperties": False,
            },
        },
        "recommendations": {
            "type": "array",
            "minItems": 1,
            "maxItems": 3,
            "items": {"type": "string"},
        },
        "summary": {"type": "string"},
    },
    "required": ["overall_status", "confidence", "findings", "recommendations", "summary"],
    "additionalProperties": False,
}


class OpenRouterError(RuntimeError):
    pass


def _validate_report(data):
    if not isinstance(data, dict):
        raise OpenRouterError("OpenRouter returned a non-object report")
    if data.get("overall_status") not in {"Normal", "Abnormal", "Requires Attention"}:
        raise OpenRouterError("OpenRouter returned an invalid overall status")
    confidence = data.get("confidence")
    if isinstance(confidence, bool) or not isinstance(confidence, (int, float)) or not 0 <= confidence <= 100:
        raise OpenRouterError("OpenRouter returned invalid confidence")
    findings = data.get("findings")
    if not isinstance(findings, list) or len(findings) != 1 or not isinstance(findings[0], dict):
        raise OpenRouterError("OpenRouter must return exactly one primary finding")
    finding = findings[0]
    required_strings = ("name", "region", "description")
    if any(not isinstance(finding.get(key), str) or not finding[key].strip() for key in required_strings):
        raise OpenRouterError("OpenRouter returned an incomplete primary finding")
    if finding.get("severity") not in {"Normal", "Mild", "Moderate", "Severe"}:
        raise OpenRouterError("OpenRouter returned an invalid severity")
    finding_confidence = finding.get("confidence")
    if (
        isinstance(finding_confidence, bool)
        or not isinstance(finding_confidence, (int, float))
        or not 0 <= finding_confidence <= 100
    ):
        raise OpenRouterError("OpenRouter returned invalid finding confidence")
    recommendations = data.get("recommendations")
    if (
        not isinstance(recommendations, list)
        or not 1 <= len(recommendations) <= 3
        or any(not isinstance(item, str) or not item.strip() for item in recommendations)
    ):
        raise OpenRouterError("OpenRouter returned invalid recommendations")
    if not isinstance(data.get("summary"), str) or not data["summary"].strip():
        raise OpenRouterError("OpenRouter returned an empty summary")
    return data


def _extract_content(response_data):
    try:
        content = response_data["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError) as exc:
        raise OpenRouterError("OpenRouter response did not contain assistant content") from exc
    if isinstance(content, list):
        content = "".join(
            part.get("text", "")
            for part in content
            if isinstance(part, dict) and isinstance(part.get("text"), str)
        )
    if not isinstance(content, str) or not content.strip():
        raise OpenRouterError("OpenRouter returned empty assistant content")
    return content


def run_via_openrouter(system_prompt, user_prompt):
    if not config.OPENROUTER_API_KEY:
        raise OpenRouterError("OPENROUTER_API_KEY is not configured")
    headers = {
        "Authorization": f"Bearer {config.OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": config.OPENROUTER_SITE_URL,
        "X-OpenRouter-Title": config.OPENROUTER_APP_NAME,
    }
    payload = {
        "model": config.OPENROUTER_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "max_tokens": config.LLM_MAX_TOKENS,
        "stream": False,
        "response_format": {
            "type": "json_schema",
            "json_schema": {
                "name": "xyra_clinical_report",
                "strict": True,
                "schema": REPORT_SCHEMA,
            },
        },
        "provider": {"require_parameters": True},
    }
    try:
        response = requests.post(
            config.OPENROUTER_API_URL,
            headers=headers,
            json=payload,
            timeout=(config.LLM_CONNECT_TIMEOUT_SECONDS, config.LLM_TIMEOUT_SECONDS),
        )
        response.raise_for_status()
    except requests.Timeout as exc:
        raise OpenRouterError("OpenRouter request timed out") from exc
    except requests.RequestException as exc:
        status_code = getattr(exc.response, "status_code", None)
        status = f" (HTTP {status_code})" if status_code else ""
        raise OpenRouterError(f"OpenRouter request failed{status}") from exc
    try:
        response_data = response.json()
    except ValueError as exc:
        raise OpenRouterError("OpenRouter returned invalid JSON transport data") from exc
    try:
        report = json.loads(_extract_content(response_data))
    except json.JSONDecodeError as exc:
        raise OpenRouterError("OpenRouter returned malformed report JSON") from exc
    return _validate_report(report)
