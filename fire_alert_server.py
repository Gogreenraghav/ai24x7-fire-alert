"""
AI24x7 Fire Alert - API Server + Dashboard
Flask API on port 5060 + Streamlit dashboard
"""
import os, json, sys
from pathlib import Path

# ─── Add parent path ────────────────────────
sys.path.insert(0, os.path.dirname(__file__))
from fire_detector import FireAlertManager, create_fire_api

# ─── Run Flask API ──────────────────────────
if __name__ == "__main__":
    import uvicorn, argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=5060)
    parser.add_argument("--host", default="0.0.0.0")
    args = parser.parse_args()
    
    manager = FireAlertManager()
    app = create_fire_api(manager)
    
    print(f"\n🔥 AI24x7 Fire Alert API running on {args.host}:{args.port}")
    print("   Endpoints:")
    print("   POST /fire/start    - Add camera to monitoring")
    print("   POST /fire/stop    - Remove camera")
    print("   GET  /fire/status  - All camera status")
    print("   POST /fire/test    - Send test alert")
    print("   GET  /fire/logs    - Alert history")
    
    uvicorn.run(app, host=args.host, port=args.port)