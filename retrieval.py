import json
import re
import faiss
import time
from sentence_transformers import SentenceTransformer
from .config import settings
from .database import ChunkDatabase

class HybridRetriever:
    def __init__(self, artifact_dir: str = None):
        # Use settings unless override provided
        self.index_path = settings.INDEX_PATH
        self.cache_path = settings.CACHE_PATH
        
        print(f"Loading RAG Index from {self.index_path}...")
        self.index = faiss.read_index(self.index_path)
        
        print(f"Loading Embedding Model {settings.EMBEDDING_MODEL}...")
        self.model = SentenceTransformer(settings.EMBEDDING_MODEL, trust_remote_code=True, device="cpu")
        
        print("Loading CAG Cache...")
        try:
            with open(self.cache_path, "r") as f:
                self.cache = json.load(f)
                
            # --- DEBUG: Verify Cache Loading ---
            ipc_count = len(self.cache.get("IPC", {}))
            bns_count = len(self.cache.get("BNS", {}))
            print(f"✅ CAG Cache Loaded: {ipc_count} IPC sections, {bns_count} BNS sections.")
            # -----------------------------------

        except FileNotFoundError:
            print("⚠️ CAG Cache not found. Starting with empty cache.")
            self.cache = {}
            
        # Initialize Database Connection Handler
        self.db = ChunkDatabase()

    def search(self, query: str, k: int = 5):
        results = []
        
        # --- LAYER 1: CAG (Statute Cache) ---
        # Improved Regex: Matches "Section 302 IPC", "IPC 302", "Sec 302", "BNS 103"
        # Group 1/2 match "302 IPC", Group 3/4 match "IPC 302"
        pattern = r"(?:(?:Section|Sec\.?)\s+)?(\d+)\s*(?:of\s+the\s+)?\s*(IPC|BNS)|(IPC|BNS)\s*(?:Section|Sec\.?)?\s*(\d+)"
        matches = re.findall(pattern, query, re.IGNORECASE)
        
        for match in matches:
            # Normalize groups: (num, stat, '', '') OR ('', '', stat, num)
            sec_num = match[0] if match[0] else match[3]
            statute_raw = match[1] if match[1] else match[2]
            
            # Normalize Statute Name
            stat_key = "BNS" if "BNS" in statute_raw.upper() else "IPC"
            
            if stat_key in self.cache and sec_num in self.cache[stat_key]:
                results.append({
                    "type": "CAG",
                    "score": 1.0,
                    "doc_id": f"{stat_key} Section {sec_num}",
                    "text": self.cache[stat_key][sec_num],
                    "source": "Statute Book"
                })

        # --- LAYER 2: RAG (Vector Search) ---
        q_emb = self.model.encode([query], convert_to_numpy=True, normalize_embeddings=True)
        D, I = self.index.search(q_emb, k)
        
        for score, idx in zip(D[0], I[0]):
            if idx == -1: continue
            
            # Fetch text from SQLite via Database Class
            chunk_data = self.db.get_chunk(int(idx))
            
            if chunk_data:
                results.append({
                    "type": "RAG",
                    "score": float(score),
                    "doc_id": chunk_data['doc_id'],
                    "text": chunk_data['text'],
                    "source": "Case Law",
                    "meta": chunk_data['meta']
                })
        
        # Prioritize CAG results at the top
        return results[:k+2]