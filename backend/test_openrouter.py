import json
import unittest
from unittest.mock import patch

import requests

import config
import chat_via_openrouter
from agents.synthesizer import SynthesizerAgent


class FakeResponse:
    def __init__(self, payload, status_code=200):
        self.payload = payload
        self.status_code = status_code

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.HTTPError(response=self)

    def json(self):
        return self.payload


class OpenRouterClientTests(unittest.TestCase):
    def setUp(self):
        self.original_key = config.OPENROUTER_API_KEY
        config.OPENROUTER_API_KEY = "test-key"

    def tearDown(self):
        config.OPENROUTER_API_KEY = self.original_key

    def valid_response(self):
        report = {
            "overall_status": "Abnormal",
            "confidence": 88,
            "findings": [
                {
                    "name": "Bacterial Pneumonia",
                    "region": "Lower lungs",
                    "severity": "Moderate",
                    "confidence": 88,
                    "description": "Findings are consistent with bacterial pneumonia.",
                }
            ],
            "recommendations": ["Consult a radiologist."],
            "summary": "Bacterial pneumonia is the primary finding.",
        }
        return {"choices": [{"message": {"content": json.dumps(report)}}]}

    def test_success(self):
        with patch.object(chat_via_openrouter.requests, "post", return_value=FakeResponse(self.valid_response())) as post:
            result = chat_via_openrouter.run_via_openrouter("system", "user")
        self.assertEqual(result["overall_status"], "Abnormal")
        self.assertEqual(post.call_args.kwargs["json"]["model"], "liquid/lfm-2.5-2.6b:free")
        self.assertEqual(post.call_args.kwargs["json"]["response_format"]["type"], "json_schema")

    def test_missing_key(self):
        config.OPENROUTER_API_KEY = ""
        with self.assertRaises(chat_via_openrouter.OpenRouterError):
            chat_via_openrouter.run_via_openrouter("system", "user")

    def test_http_error(self):
        error = FakeResponse({}, status_code=429)
        with patch.object(chat_via_openrouter.requests, "post", return_value=error):
            with self.assertRaisesRegex(chat_via_openrouter.OpenRouterError, "HTTP 429"):
                chat_via_openrouter.run_via_openrouter("system", "user")

    def test_timeout(self):
        with patch.object(chat_via_openrouter.requests, "post", side_effect=requests.Timeout()):
            with self.assertRaisesRegex(chat_via_openrouter.OpenRouterError, "timed out"):
                chat_via_openrouter.run_via_openrouter("system", "user")

    def test_malformed_report(self):
        response = {"choices": [{"message": {"content": "not-json"}}]}
        with patch.object(chat_via_openrouter.requests, "post", return_value=FakeResponse(response)):
            with self.assertRaises(chat_via_openrouter.OpenRouterError):
                chat_via_openrouter.run_via_openrouter("system", "user")

    def test_synthesis_uses_model_confidence(self):
        response = self.valid_response()
        response["choices"][0]["message"]["content"] = json.dumps(
            {
                "overall_status": "Abnormal",
                "confidence": 5,
                "findings": [
                    {
                        "name": "Bacterial Pneumonia",
                        "region": "Lungs",
                        "severity": "Moderate",
                        "confidence": 5,
                        "description": "Bacterial pneumonia.",
                    }
                ],
                "recommendations": ["Consult a radiologist."],
                "summary": "Bacterial pneumonia.",
            }
        )
        diagnosis = {"label": "BACTERIAL", "confidence_score": 0.82, "model_version": "test"}
        with patch("agents.synthesizer.run_via_openrouter", return_value=json.loads(response["choices"][0]["message"]["content"])):
            result = SynthesizerAgent().run(diagnosis, {}, [])
        self.assertEqual(result["confidence"], 0.82)
        self.assertEqual(result["findings"][0]["confidence"], 0.82)

    def test_synthesis_rejects_conflicting_finding(self):
        report = {
            "overall_status": "Abnormal",
            "confidence": 90,
            "findings": [
                {
                    "name": "Viral Pneumonia",
                    "region": "Lungs",
                    "severity": "Moderate",
                    "confidence": 90,
                    "description": "Viral pneumonia.",
                }
            ],
            "recommendations": ["Consult a radiologist."],
            "summary": "Viral pneumonia.",
        }
        diagnosis = {"label": "BACTERIAL", "confidence_score": 0.82, "model_version": "test"}
        with patch("agents.synthesizer.run_via_openrouter", return_value=report):
            result = SynthesizerAgent().run(diagnosis, {}, [])
        self.assertIn("fallback", result["summary"].lower())
        self.assertEqual(result["confidence"], 0.82)


if __name__ == "__main__":
    unittest.main()
