# Configuration

infoflow is deployed from `hopsakee-server`: the compose file, the volume layout and
the secret delivery all live in `config/infoflow/` and `server_setup/` there, together
with `DEPLOYING.md`, which is the authoritative deployment guide. This file documents
only what the app itself reads.

| Variable | Default | Purpose |
| --- | --- | --- |
| `SESSION_SECRET` | – | Key used to sign session cookies. The app refuses to start without it. |
| `SESSION_SECRET_FILE` | – | File to read the session key from, for a secret mounted as a file rather than passed in the environment. |
| `INFOFLOW_DB_PATH` | `data/infoflow.db` under the project root | SQLite file. The image sets this to `/data/infoflow.db`; mount the app's own data directory there. |
| `INFOFLOW_HTTPS_ONLY` | `0` | Set to `1` when the app is reached over HTTPS, so the session cookie is marked `Secure`. |
| `INFOFLOW_DEV` | `0` | Local development: enables the uvicorn auto-reloader and generates a random session key. Never set it in a deployment. |
| `PORT` | `5001` | Port to listen on. |

The session key is passed to `fast_app(secret_key=...)`, so FastHTML never calls
`get_key()` and never writes a `.sesskey`. That matters beyond tidiness: the container
runs as an unprivileged user with a root-owned `/app`, and the write would fail at
import time.

Two keys previously lived in committed `.sesskey` files. They are in git history, so
treat them as public and never reuse them.

## Local development

```bash
uv sync
INFOFLOW_DEV=1 uv run main.py
```

Without `INFOFLOW_DEV` the app runs as it does in the container: no reloader, and a
session key required.
