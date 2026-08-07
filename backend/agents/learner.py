import json
import os
import threading
from datetime import datetime, timezone

import config


class LearnerAgent:
    """Module 6: Asynchronous active learning case curation."""

    def __init__(self):
        self.log_path = config.CASE_LOG_PATH
        os.makedirs(os.path.dirname(self.log_path), exist_ok=True)
        self._lock = threading.Lock()

    def log_async(self, case_data: dict):
        thread = threading.Thread(
            target=self._write_case, args=(case_data,), daemon=True
        )
        thread.start()

    def _write_case(self, case_data: dict):
        try:
            entry = {
                "case_id": case_data.get("case_id", "unknown"),
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "label": case_data.get("diagnosis", {}).get("label", "Unknown"),
                "confidence": case_data.get("diagnosis", {}).get("confidence_score", 0.0),
                "retry_count": case_data.get("validation", {}).get("retry_count", 0),
                "pipeline_status": case_data.get("pipeline_status", "UNKNOWN"),
                "user_override": None,
                "hard_case": self._is_hard_case(case_data),
                "image_path": case_data.get("image_path", ""),
            }

            line = json.dumps(entry, ensure_ascii=False) + "\n"
            with self._lock:
                with open(self.log_path, "a", encoding="utf-8") as f:
                    f.write(line)
                    f.flush()

            if entry["hard_case"]:
                self._flag_hard_case(entry)

        except Exception as e:
            print(f"[Learner] Failed to log case: {e}")

    def _is_hard_case(self, case_data: dict) -> bool:
        conf = case_data.get("diagnosis", {}).get("confidence_score", 0.0)
        retry_count = case_data.get("validation", {}).get("retry_count", 0)
        pipeline_status = case_data.get("pipeline_status", "")

        if 0.50 <= conf <= 0.75:
            return True
        if retry_count > 0:
            return True
        if pipeline_status == "RETRY":
            return True
        return False

    def _flag_hard_case(self, entry: dict):
        flag_path = os.path.join(os.path.dirname(self.log_path), "hard_cases.jsonl")
        try:
            line = json.dumps(entry, ensure_ascii=False) + "\n"
            with self._lock:
                with open(flag_path, "a", encoding="utf-8") as f:
                    f.write(line)
                    f.flush()
            print(f"[Learner] Hard case flagged: {entry['case_id']}")
        except Exception as e:
            print(f"[Learner] Failed to flag hard case: {e}")

    def get_stats(self) -> dict:
        total = 0
        hard = 0
        try:
            with open(self.log_path, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        entry = json.loads(line)
                        total += 1
                        if entry.get("hard_case"):
                            hard += 1
        except FileNotFoundError:
            pass

        return {"total_cases": total, "hard_cases": hard}
