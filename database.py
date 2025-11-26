import sqlite3
import json
from typing import Optional, Dict
from .config import settings

class ChunkDatabase:
    def __init__(self):
        self.db_path = settings.DB_PATH

    def get_chunk(self, chunk_id: int) -> Optional[Dict]:
        """
        Retrieves text and metadata for a specific vector ID.
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                # We query by 'id' which matches the FAISS index integer ID
                cursor.execute(
                    "SELECT doc_id, text, meta FROM chunks WHERE id=?", 
                    (chunk_id,)
                )
                row = cursor.fetchone()
                
                if row:
                    return {
                        "doc_id": row[0],
                        "text": row[1],
                        "meta": json.loads(row[2]) if row[2] else {}
                    }
                return None
        except sqlite3.Error as e:
            print(f"Database Error: {e}")
            return None