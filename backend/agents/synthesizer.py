import re
import requests
import json

import config


class SynthesizerAgent:
    """Module 4b: LLM-based clinical narrative synthesis via OpenCode API."""

    SYSTEM_PROMPT = """You are an expert radiologist AI assistant specializing in chest X-ray interpretation.
You will receive diagnostic data from a pneumonia detection model, explainability outputs,
and relevant clinical guidelines from medical literature.

Your task is to synthesize this information into a structured clinical report.
You MUST respond with ONLY a valid JSON object using this exact structure:
{
  "overall_status": "Normal or Abnormal or Requires Attention",
  "confidence": <number 0-100>,
  "findings": [
    {
      "name": "Primary finding name (e.g. Viral Pneumonia, Bacterial Pneumonia, Normal)",
      "region": "Anatomical region",
      "severity": "Normal or Mild or Moderate or Severe",
      "confidence": <number 0-100>,
      "description": "Detailed description of the primary finding only"
    }
  ],
  "recommendations": ["Recommendation 1", "Recommendation 2"],
  "summary": "Overall clinical summary paragraph"
}

IMPORTANT RULES:
- List ONLY the PRIMARY finding detected by the model (the diagnosis label).
- Do NOT include differential diagnoses, alternative conditions, or speculative findings.
- Do NOT add multiple findings — only the single primary diagnosis from the model output.
- Keep descriptions focused on the detected finding only."""

    def __init__(self):
        self.api_url = config.LLM_API_URL
        self.api_key = config.LLM_API_KEY
        self.model = config.LLM_MODEL
        self.max_tokens = config.LLM_MAX_TOKENS

    def run(
        self,
        diagnosis: dict,
        explainability: dict,
        rag_context: list[str],
    ) -> dict:
        prompt = self._build_prompt(diagnosis, explainability, rag_context)

        try:
            response = requests.post(
                self.api_url,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "HTTP-Referer": "https://opencode.ai/",
                    "X-Title": "opencode",
                    "Content-Type": "application/json",
                },
                json={
                    "model": self.model,
                    "messages": [
                        {"role": "system", "content": self.SYSTEM_PROMPT},
                        {"role": "user", "content": prompt},
                    ],
                    "max_tokens": self.max_tokens,
                },
                timeout=30,
            )
            response.raise_for_status()

            result = response.json()
            content = result["choices"][0]["message"]["content"]

            if not content or not content.strip():
                print(f"[Synthesizer] LLM returned empty response. Full JSON:\n{json.dumps(result, indent=2)[:3000]}")
                return self.fallback_synthesis(diagnosis, explainability)

            print(f"[Synthesizer] Raw LLM response:\n{content[:2000]}")

            parsed = self._parse_response(content)
            print(f"[Synthesizer] Parsed findings count: {len(parsed.get('findings', []))}")
            return parsed

        except requests.exceptions.RequestException as e:
            print(f"[Synthesizer] API request failed: {e}")
            return self.fallback_synthesis(diagnosis, explainability)
        except (KeyError, IndexError, json.JSONDecodeError) as e:
            print(f"[Synthesizer] Response parse error: {e}")
            return self.fallback_synthesis(diagnosis, explainability)

    def _build_prompt(self, diagnosis: dict, explainability: dict, rag_context: list[str]) -> str:
        parts = [
            "## Diagnostic Model Output",
            f"- Label: {diagnosis.get('label', 'Unknown')}",
            f"- Confidence: {diagnosis.get('confidence_score', 0):.1%}",
            f"- Model: {diagnosis.get('model_version', 'N/A')}",
            "",
            "## Explainability Data",
        ]

        if explainability.get("grad_cam_url"):
            parts.append("- Grad-CAM heatmap generated (region of interest identified)")
        if explainability.get("shap_url"):
            parts.append("- SHAP pixel-level attribution generated (positive/negative contributions mapped)")


        if rag_context:
            parts.append("")
            parts.append("## Relevant Clinical Guidelines")
            for i, ctx in enumerate(rag_context[:5], 1):
                truncated = ctx[:500] + "..." if len(ctx) > 500 else ctx
                parts.append(f"{i}. {truncated}")

        parts.append("")
        parts.append(
            "Based on the above data, provide your structured clinical analysis as JSON."
        )

        return "\n".join(parts)

    def _parse_response(self, content: str) -> dict:

        cleaned = content.strip()

        code_block = re.search(r"```(?:json)?\s*\n?(.*?)\n?```", cleaned, re.DOTALL)
        if code_block:
            cleaned = code_block.group(1).strip()

        json_match = re.search(r"\{.*\}", cleaned, re.DOTALL)
        if json_match:
            try:
                parsed = json.loads(json_match.group())

                if "findings" in parsed:
                    raw = parsed["findings"]
                    if isinstance(raw, list):
                        parsed["findings"] = raw
                    elif isinstance(raw, str) and raw.strip():
                        parsed["findings"] = [{
                            "name": raw[:100],
                            "region": "Lungs",
                            "severity": "Moderate",
                            "confidence": parsed.get("confidence", 50),
                            "description": raw,
                        }]
                    elif isinstance(raw, dict):
                        parsed["findings"] = [raw]
                    else:
                        parsed["findings"] = []
                else:
                    parsed["findings"] = []

                if "recommendations" not in parsed:
                    parsed["recommendations"] = []
                if "summary" not in parsed:
                    parsed["summary"] = ""
                parsed.pop("differential_diagnosis", None)

                return parsed
            except json.JSONDecodeError:
                pass

        return {
            "overall_status": "Analysis Complete",
            "confidence": 0,
            "findings": [],
            "recommendations": ["Consult with a qualified radiologist"],
            "summary": "LLM synthesis was unable to produce structured output. Please rely on the model prediction and explainability maps above.",
        }

    def fallback_synthesis(self, diagnosis: dict, explainability: dict) -> dict:
        label = diagnosis.get("label", "Unknown")
        conf = diagnosis.get("confidence_score", 0.0)

        if label in ("BACTERIAL", "VIRAL"):
            status = "Abnormal"
            severity = "Moderate" if conf > 0.7 else "Mild"
        elif label == "NORMAL":
            status = "Normal"
            severity = "Normal"
        else:
            status = "Requires Attention"
            severity = "Mild"

        conf_pct = int(conf * 100)

        return {
            "overall_status": status,
            "confidence": conf_pct,
            "findings": [
                {
                    "name": f"Model Prediction: {label}",
                    "region": "Lungs",
                    "severity": severity,
                    "confidence": conf_pct,
                    "description": (
                        f"The CNN model predicted '{label}' with "
                        f"{conf:.1%} confidence. LLM synthesis was unavailable; "
                        f"this is a fallback response based on raw model output."
                    ),
                }
            ],
            "recommendations": [
                "Consult with a qualified radiologist for clinical interpretation",
                "LLM synthesis service was unavailable — manual review recommended",
            ],
            "summary": (
                f"Fallback analysis: CNN model predicted {label} with "
                f"{conf:.1%} confidence. The LLM synthesis step failed. "
                f"Please review the model output and explainability maps manually."
            ),
        }
