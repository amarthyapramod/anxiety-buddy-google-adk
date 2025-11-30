import json
import os
from datetime import datetime
from ..utils.timestamp import timestamp

class MemoryAgent:
    def __init__(self, path="/kaggle/working/src/data/sample_logs.json"):
        self.path = path
        if not os.path.exists(self.path):
            with open(self.path, "w") as f:
                json.dump([], f)

    def _read(self):
        with open(self.path, "r") as f:
            try:
                return json.load(f)
            except:
                return []

    def _write(self, data):
        with open(self.path, "w") as f:
            json.dump(data, f, indent=2)

    def save_entry(self, user_id, text, detector_out, intervention=None, notes=None, session_id=None):
        data = self._read()
        entry = {
            "id": timestamp(),
            "user_id": user_id,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "text": text,
            "emotion": detector_out.get("emotion"),
            "intensity": detector_out.get("intensity"),
            "trigger_tags": detector_out.get("trigger_tags"),
            "intervention": intervention,
            "notes": notes or ""
        }
        data.append(entry)
        self._write(data)
        return entry

    def load_last_n(self, n=7):
        return self._read()[-n:]

    def compact_summary(self, last_k=30):
        data = self._read()[-last_k:]
        if not data:
            return "No memory yet."
        emotions = {}
        total = 0
        for d in data:
            emotions[d.get("emotion", "neutral")] = emotions.get(d.get("emotion", "neutral"), 0) + 1
            total += d.get("intensity", 0)
        avg = total / max(1, len(data))
        top = ", ".join([f"{k}({v})" for k, v in sorted(emotions.items(), key=lambda x: x[1], reverse=True)[:3]])
        return f"Last {len(data)} entries avg intensity {avg:.2f}. Common: {top}."