# Persona Registry API

Initial implementation scaffold for the v1 design spec.

## Run

```bash
pip install -e .
uvicorn app.main:app --reload
```

On Windows, you can also use:

```bash
scripts\start_server.cmd
```

Default persistence is SQLite at `./data/persona_registry.db`.

To override the database location:

```bash
set PERSONA_REGISTRY_DB_URL=sqlite:///./data/local-dev.db
uvicorn app.main:app --reload
```

## Test

### Web UI Test Page

Open `web/index.html` in your browser to test the API interactively. Configure the API base URL at the top of the page (default: `http://localhost:8000`).

### Programmatic Tests

```bash
pip install -e .[dev]
pytest
```

Tests create isolated SQLite databases per case so API behavior remains deterministic.

## Server Control Helpers

- `scripts\start_server.cmd` starts the API server using the project virtual environment.
- `scripts\reload_server.cmd` triggers a reload by updating the reload trigger module.
- `scripts\start_tunnel.py` starts a Cloudflare tunnel to your local API and prints the public URL.
- The web test page includes **Start Server**, **Reload Server**, **Generate Cloudflare URL**, and **Stop Tunnel** buttons in the **Server Controls** section.
- The admin page also shows separate live badges for **Server Status** and **Tunnel Status**.
- Generated tunnel URLs are shown in **Current Tunnel URL** and can be copied with **Copy URL**.

## API Key (optional)

If you want to protect all `/v1/*` endpoints with an API key:

```bash
set PERSONA_REGISTRY_API_KEY=your-secret-key
uvicorn app.main:app --reload
```

Then clients must send header:

```text
X-API-Key: your-secret-key
```

### Tunnel Helper

```bash
c:/Users/godda/personashare/.venv/Scripts/python.exe scripts/start_tunnel.py
```

Optional target URL override:

```bash
c:/Users/godda/personashare/.venv/Scripts/python.exe scripts/start_tunnel.py --url http://127.0.0.1:8000
```

## GitHub Pages (for Alex)

1. Prepare the static site files:

```bash
c:/Users/godda/personashare/.venv/Scripts/python.exe scripts/prepare_github_pages.py
```

2. Commit and push these files:
- `docs/index.html`
- `docs/.nojekyll`

3. In GitHub repo settings:
- Go to **Settings -> Pages**
- Set **Source** to `Deploy from a branch`
- Set **Branch** to `main` and **Folder** to `/docs`
- Save

4. Your UI URL will be:
- `https://<your-github-username>.github.io/<your-repo-name>/`

5. In the hosted UI (`docs/index.html` hybrid client):
- Set **Backend Mode** to `Remote API (Cloudflare URL)`.
- Paste your tunnel URL (`https://...trycloudflare.com`) in the API URL field.
- If API key is enabled, paste it in the API key input (`X-API-Key`).
- Click **Test** and then use the page normally.

6. Offline fallback in hosted UI:
- Click **Create Offline Copy** to snapshot remote personas/rosters into browser local storage.
- Switch back to local mode automatically if your tunnel/API goes offline.

## Implemented endpoints

- `POST /v1/personas`
- `POST /v1/personas:import`
- `GET /v1/personas`
- `GET /v1/personas/{id}`
- `GET /v1/personas/{slug}/versions`
- `GET /v1/personas/{slug}/versions/{version}`
- `GET /v1/personas/{slug}/latest`
- `PATCH /v1/personas/{id}` (draft only)
- `POST /v1/personas/{id}:publish`
- `POST /v1/personas/{id}:deprecate`
- `POST /v1/personas/{id}:archive`
- `POST /v1/rosters`
- `GET /v1/rosters`
- `GET /v1/rosters/{roster_id}`
- `PATCH /v1/rosters/{roster_id}`
- `DELETE /v1/rosters/{roster_id}`
- `POST /v1/evaluations`
- `GET /v1/evaluations/{evaluation_id}`
- `GET /v1/evaluations/{evaluation_id}/results`
- `POST /v1/evaluations:compare`

## Storage

- SQLite + SQLModel persistence for personas, rosters, and evaluations
- App factory available via `app.main.create_app(database_url=...)` for tests and alternate deployments
