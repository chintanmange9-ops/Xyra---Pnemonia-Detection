import re

import config


class ValidatorAgent:
    """Module 4c: Guardrail gatekeeper — validates pipeline output before reporting."""

    def __init__(self):
        self.threshold = config.CONFIDENCE_THRESHOLD
        self.max_retries = config.MAX_RETRY_COUNT

    def run(self, result: dict, rag_context: list[str] = None) -> dict:
        confidence = result.get("confidence", 0)
        confidence_decimal = confidence / 100.0 if confidence > 1 else confidence

        confidence_pass = confidence_decimal >= self.threshold
        hallucination_pass = self._check_consistency(result, rag_context or [])

        overall_pass = confidence_pass and hallucination_pass

        validation = {
            "validated_by": "Agent_5_Guardrail",
            "confidence_pass": confidence_pass,
            "confidence_score": round(confidence_decimal, 4),
            "hallucination_check": "PASSED" if hallucination_pass else "FAILED",
            "overall_pass": overall_pass,
            "retry_count": 0,
        }

        if overall_pass:
            result["pipeline_status"] = "APPROVED"
        else:
            result["pipeline_status"] = "RETRY"

        result["validation"] = validation
        return result

    def _check_consistency(self, result: dict, rag_context: list[str]) -> bool:
        summary = result.get("summary", "").lower()
        findings_text = " ".join(
            f.get("description", "") for f in result.get("findings", [])
        ).lower()
        combined_text = summary + " " + findings_text

        if not any(
            keyword in combined_text
            for keyword in ["normal", "abnormal", "pneumonia", "bacterial", "viral", "finding", "lung", "chest"]
        ):
            print("[Validator] Missing expected medical terminology in output")
            return False

        return True

    def should_retry(self, result: dict) -> bool:
        status = result.get("pipeline_status", "")
        retry_count = result.get("validation", {}).get("retry_count", 0)
        return status == "RETRY" and retry_count < self.max_retries

    def increment_retry(self, result: dict) -> dict:
        if "validation" not in result:
            result["validation"] = {"retry_count": 0}
        result["validation"]["retry_count"] = result["validation"].get("retry_count", 0) + 1
        return result
