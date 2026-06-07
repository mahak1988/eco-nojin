"""حافظه برداری محلی بدون نیاز به Qdrant"""
import json
from pathlib import Path
from typing import Any, Dict, List

import numpy as np
import structlog
from sentence_transformers import SentenceTransformer

logger = structlog.get_logger()


class LocalVectorMemory:
    def __init__(self, storage_path: str = "agents/memory/vectors.json"):
        self.storage_path = Path(storage_path)
        self.encoder = SentenceTransformer("./models/all-MiniLM-L6-v2")
        self.logger = logger.bind(component="local_vector_memory")
        self.vectors = []
        self.metadata = []
        self._load_data()

    def _load_data(self):
        if self.storage_path.exists():
            with open(self.storage_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.vectors = [np.array(v) for v in data.get("vectors", [])]
                self.metadata = data.get("metadata", [])

    def _save_data(self):
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.storage_path, "w", encoding="utf-8") as f:
            json.dump(
                {"vectors": [v.tolist() for v in self.vectors], "metadata": self.metadata},
                f,
                ensure_ascii=False,
                indent=2,
            )

    def store(self, text: str, metadata: Dict[str, Any] = None):
        embedding = self.encoder.encode(text)
        self.vectors.append(embedding)
        self.metadata.append({"text": text, "metadata": metadata or {}})
        self._save_data()
        self.logger.info("text_stored", text_length=len(text))

    def search(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        if not self.vectors:
            return []
        query_embedding = self.encoder.encode(query)
        similarities = []
        for i, vector in enumerate(self.vectors):
            sim = np.dot(query_embedding, vector) / (
                np.linalg.norm(query_embedding) * np.linalg.norm(vector)
            )
            similarities.append((sim, i))
        similarities.sort(reverse=True)
        return [
            {
                "text": self.metadata[idx]["text"],
                "score": float(score),
                "metadata": self.metadata[idx]["metadata"],
            }
            for score, idx in similarities[:limit]
        ]


if __name__ == "__main__":
    memory = LocalVectorMemory()
    memory.store("NDVI شاخص پوشش گیاهی است", {"type": "definition"})
    memory.store("AquaCrop مدل شبیهسازی رشد محصول است", {"type": "model"})
    results = memory.search("شاخصهای ماهوارهای چیست", limit=2)
    print("\n🔍 Search Results:")
    for r in results:
        print(f"  Score: {r['score']:.3f} | {r['text'][:80]}...")
