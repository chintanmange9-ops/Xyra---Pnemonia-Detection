import threading
import time
import unittest
from unittest.mock import patch

from agents.rag_agent import RAGAgent
from agents.synthesizer import SynthesizerAgent
from agents.validator import ValidatorAgent
from pipeline.orchestrator import PipelineOrchestrator


class RAGInitializationTests(unittest.TestCase):
    def test_warmup_initializes_once_across_threads(self):
        agent = RAGAgent()
        calls = []

        def slow_initialize():
            calls.append(1)
            time.sleep(0.05)

        agent._load_or_build_index = slow_initialize
        threads = [threading.Thread(target=agent.warmup) for _ in range(8)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

        self.assertEqual(len(calls), 1)
        self.assertTrue(agent._initialized)


class DegradedSynthesisTests(unittest.TestCase):
    def test_fallback_result_is_not_mapped_as_validated(self):
        orchestrator = object.__new__(PipelineOrchestrator)
        full_result = orchestrator._fallback_result(
            {"label": "NORMAL", "confidence_score": 0.82, "probabilities": {}},
            {},
            "PX-TEST",
        )
        frontend = orchestrator._map_to_frontend(full_result, [])

        self.assertEqual(frontend["status"], "FALLBACK")
        self.assertFalse(frontend["isValidated"])

    def test_validator_rejects_fallback_synthesis(self):
        result = {
            "confidence": 0.82,
            "synthesis_status": "fallback",
            "summary": "CNN model predicted NORMAL with high confidence.",
            "findings": [{"description": "Normal lungs"}],
        }
        validated = ValidatorAgent().run(result, ["Normal lungs"])

        self.assertEqual(validated["pipeline_status"], "FALLBACK")
        self.assertFalse(validated["validation"]["overall_pass"])

    def test_successful_synthesis_is_marked_complete(self):
        diagnosis = {"label": "NORMAL", "confidence_score": 0.82, "model_version": "test"}
        report = {
            "overall_status": "Normal",
            "confidence": 90,
            "findings": [
                {
                    "name": "Normal",
                    "region": "Lungs",
                    "severity": "Normal",
                    "confidence": 90,
                    "description": "No focal pneumonia finding.",
                }
            ],
            "recommendations": ["Routine professional review."],
            "summary": "Normal chest X-ray.",
        }
        with patch("agents.synthesizer.run_via_openrouter", return_value=report):
            result = SynthesizerAgent().run(diagnosis, {}, [])

        self.assertEqual(result["synthesis_status"], "openrouter")
        self.assertEqual(result["confidence"], 0.82)


if __name__ == "__main__":
    unittest.main()
