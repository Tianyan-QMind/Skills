"""Start the materialized inference-only QML application."""

import sys
from pathlib import Path

APPLICATION_ROOT = Path(__file__).resolve().parents[1]
if str(APPLICATION_ROOT) not in sys.path:
    sys.path.insert(0, str(APPLICATION_ROOT))

from backend.main import app, resolve_network  # noqa: E402, I001


if __name__ == "__main__":
    import uvicorn

    host, port = resolve_network()
    uvicorn.run(app, host=host, port=port)
