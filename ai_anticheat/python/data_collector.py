# python/data_collector.py

import json
import os
import uuid
from datetime import datetime

def record_session(player_id, entries, vector_type, output_dir="logs"):
    os.makedirs(output_dir, exist_ok=True)
    session_id = str(uuid.uuid4())
    meta = {
        "session_id": session_id,
        "player_id": player_id,
        "vector": vector_type,
        "timestamp": datetime.utcnow().isoformat()
    }
    with open(f"{output_dir}/{session_id}.json", "w") as f:
        json.dump({"meta": meta, "entries": entries}, f)
