import os
import glob

class RAG:
    def __init__(self, path="/kaggle/working/src/data/rag"):
        self.path = path
        self.docs = []
        self._load()

    def _load(self):
        self.docs = []
        if not os.path.exists(self.path):
            return
        for fn in glob.glob(os.path.join(self.path, "*.txt")):
            with open(fn, "r", encoding="utf-8") as f:
                self.docs.append({"file": os.path.basename(fn), "text": f.read().strip()})

    def doc_count(self):
        return len(self.docs)

    def retrieve(self, query, top_k=1):
        q_tokens = set(query.lower().split())
        scored = []
        for d in self.docs:
            score = len(q_tokens & set(d["text"].lower().split()))
            scored.append((score, d["text"]))
        scored.sort(key=lambda x: x[0], reverse=True)
        results = [s[1] for s in scored if s[0] > 0]
        return results[:top_k] if results else ([self.docs[0]["text"]] if self.docs else [""])
