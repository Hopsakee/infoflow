# Deploying infoflow

infoflow is a small single-user web app. It needs exactly two things from its
host: **its own SQLite file** and **its own session key**. It does not need root,
it does not need a code reloader, and it must never be given access to secrets
belonging to other services.

## Quick start

```bash
mkdir -p secrets
python -c "import secrets; print(secrets.token_hex(32))" > secrets/infoflow_session_key
sudo chown 10001:10001 secrets/infoflow_session_key   # the uid the container runs as
chmod 400 secrets/infoflow_session_key

docker compose up -d --build
```

`compose.yaml` is the reference deployment. It runs the container as uid 10001
with a read-only root filesystem, all capabilities dropped and
`no-new-privileges`, mounts a dedicated `infoflow-data` volume at `/data`, and
mounts the session key read-only as a single file at
`/run/secrets/infoflow_session_key`.

## Configuration

| Variable | Default | Purpose |
| --- | --- | --- |
| `INFOFLOW_DB_PATH` | `data/infoflow.db` under the project root | SQLite file. Set to a path on the app's own writable volume, e.g. `/data/infoflow.db`. |
| `INFOFLOW_SESSION_KEY` | – | Key used to sign session cookies. |
| `INFOFLOW_SESSION_KEY_FILE` | – | File to read the session key from; use this with a read-only mounted secret instead of putting the key in the environment. |
| `INFOFLOW_HTTPS_ONLY` | `0` | Set to `1` when the app is reached over HTTPS, so the session cookie is marked `Secure`. |
| `INFOFLOW_DEV` | `0` | Set to `1` for the uvicorn auto-reloader. Local development only - it watches and re-executes source on change, so it never belongs in a deployment. |
| `PORT` | `5001` | Port to listen on. |

If neither `INFOFLOW_SESSION_KEY` nor `INFOFLOW_SESSION_KEY_FILE` is set, the app
generates a random key at startup and warns. That is safe but means sessions end
whenever the app restarts, so set one for anything long-lived.

## Mounts: what the container may and may not see

- **Yes:** one read-write volume for `/data`, holding only `infoflow.db`. A fresh
  named volume inherits `/data`'s ownership from the image, so it works as is; a
  host bind mount needs `chown 10001:10001` first.
- **Yes:** one read-only file with infoflow's own session key.
- **No:** a shared secrets volume, and never read-write. A container that can read
  a shared secrets volume can read every password hash, session key and API key on
  the host, and a read-write mount lets it rewrite them. infoflow has no use for
  any of that.

## Rotating the session key

The key previously lived in a committed `.sesskey` file, so it has to be treated
as public. Anyone holding it can forge session cookies. Generate a new one as
shown above and restart the app; existing sessions are invalidated, which is the
intent. The old value stays in git history - it is worthless once rotated, but
don't reuse it anywhere.

## Local development

```bash
uv sync
INFOFLOW_DEV=1 uv run main.py
```

Without `INFOFLOW_DEV` the app runs the same way it does in the container: no
reloader.
