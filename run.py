"""
run.py
Convenience entry point to start the AI-Powered Agriculture Crop Advisory Assistant.

Usage:
    python run.py                  # Start with default settings (host/port from .env)
    python run.py --port 8080      # Start on a custom port
    python run.py --no-reload      # Disable hot-reload (for production-like demo)

The server will:
  1. Load environment settings from .env
  2. Auto-initialize FAISS + keyword search indexes if they don't exist on disk
  3. Auto-train ML models if model files are not found
  4. Serve the dashboard at http://localhost:8000/
  5. Serve the API at http://localhost:8000/docs (Swagger UI)
"""

import argparse
import uvicorn
from app.config.settings import settings

def main():
    parser = argparse.ArgumentParser(
        description="AI-Powered Agriculture Crop Advisory Assistant",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    parser.add_argument("--host", default=str(settings.HOST), help="Bind address (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=settings.PORT, help="Port to listen on (default: 8000)")
    parser.add_argument("--no-reload", dest="reload", action="store_false", help="Disable auto-reload")
    parser.set_defaults(reload=settings.DEBUG)

    args = parser.parse_args()

    print("=" * 70)
    print("  AI-Powered Agriculture Crop Advisory Assistant")
    print("  Capstone Project v1.0 - Production-Style Implementation")
    print("=" * 70)
    print(f"  -> Dashboard:   http://{args.host}:{args.port}/")
    print(f"  -> Swagger API: http://{args.host}:{args.port}/docs")
    print(f"  -> ReDoc:       http://{args.host}:{args.port}/redoc")
    print(f"  -> Auto-Reload: {args.reload}")
    print("=" * 70)

    uvicorn.run(
        "app.main:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
        log_level="info"
    )

if __name__ == "__main__":
    main()
