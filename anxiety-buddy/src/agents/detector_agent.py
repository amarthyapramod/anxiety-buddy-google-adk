import json
from ..utils.llm_wrapper import llm_call

FALLBACK_KEYWORDS = {
    "panic": ["panic", "can't breathe", "chest racing", "heart racing"],
    "anxious": ["anxious", "anxiety", "worried", "nervous"],
    "stressed": ["stressed", "overwhelmed"],
    "sad": ["sad", "depressed", "down"],
    "positive": ["good", "great", "okay", "well"]
}

class DetectorAgent:
    def __init__(self, use_llm=True, model_kwargs=None):
        self.use_llm = use_llm
        self.model_kwargs = model_kwargs or {}

    def _fallback_classify(self, text):
        text_l = text.lower()
        emotion = "neutral"
        for e, keywords in FALLBACK_KEYWORDS.items():
            for kw in keywords:
                if kw in text_l:
                    emotion = e
                    break
            if emotion != "neutral":
                break

        intensity = {"panic": 5, "anxious": 3, "stressed": 3, "sad": 2, "positive": 1}.get(emotion, 0)
        needs_intervention = intensity >= 4 or emotion == "panic"
        
        return {
            "emotion": emotion,
            "intensity": intensity,
            "trigger_tags": [],
            "needs_intervention": needs_intervention
        }

    def classify(self, text):
        if self.use_llm:
            prompt = f"""Classify emotion from text. Return ONLY JSON:
{{"emotion": "panic|anxious|stressed|sad|neutral|positive", "intensity": 0-5, "trigger_tags": [], "needs_intervention": true|false}}

Text: "{text}"

JSON:"""
            try:
                out = llm_call(prompt, **(self.model_kwargs))
                out = out.replace("```json", "").replace("```", "").strip()
                return json.loads(out)
            except:
                return self._fallback_classify(text)
        return self._fallback_classify(text)