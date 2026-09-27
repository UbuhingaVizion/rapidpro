# AGENTS.md

## What this repo is (read first)
- Django project `temba/` — the RapidPro web app (lineage: RapidPro v7.4.2). This is the
  **UbuhingaVizion fork**, whose whole point is to keep **RapidPro Surveyor** working as an
  **offline client that runs the GoFlow engine on-device**. Upstream removed Surveyor and its
  server support; do not "clean up" Surveyor code.
- Branches: `develop` = working branch (RapidPro 7.4.2 + local Python 3.12/uv upgrades);
  `master` mirrors upstream `rapidpro/rapidpro`. Upstream layout differs (upstream `main` has
  no `.haml`; this tree still does). Do not assume upstream state.
- This repo is only the web app. Flow execution, channel I/O, search, and archiving are
  **separate services** this app is tightly version-coupled to (see below).
- UI templates are **HAML** (`*.haml`, django-hamlpy), not Django HTML.

## Component coupling (critical — never upgrade one in isolation)
RapidPro must run with a **matching train** of companion services. Bumping any one independently
breaks the others; move them together and re-test.
- **Mailroom** (Go) — flow execution + Surveyor submission endpoint. Schema-coupled to this
  repo's migrations: `develop` uses `flows_flowsession.connection_id`, while Mailroom switched
  to `call_id` in `v7.5.14`. `/mr/surveyor/submit` exists only in Mailroom `<= 9.1.9`
  (removed upstream in 9.1.10). CI pins one version; the deployed compose pins another.
- **Courier** (Go) — channel send/receive; versioned to follow the Mailroom train.
- **GoFlow** (Go) — the flow engine. Runs server-side inside Mailroom, and **offline inside the
  Surveyor Android app** (bundled `goflow.aar`). Server/client spec must stay aligned.
- **rp-indexer** — message/contact search indexing.
- **rp-archiver** — archives old runs/messages to S3.
- Flow spec: `develop` exports `CURRENT_SPEC_VERSION = 13.1.0`; the Surveyor engine supports
  only **spec <= 13.x**. Keep published survey flows within that range.
- Where versions are declared (sources of truth): `.github/workflows/ci.yml` (mailroom,
  rp-indexer), the committed root binaries, and the sibling `UbuhingaVizion/rapidpro-docker`
  compose (mailroom/courier/rp-indexer/rp-archiver/ES/PostGIS/Redis). No component pins live
  in `pyproject.toml` except the Django app's own deps.

## Setup
- Python 3.12 + `uv` (PEP 621 + `uv.lock`). Create env: `uv sync --frozen`.
- `temba/settings.py` is a symlink to `temba/settings.py.dev`. If missing:
  `ln -s temba/settings.py.dev temba/settings.py` (CI does this).
- Env: direnv loads `.envrc` -> `.env` (needs `DATABASE_URL`); `DEBUG=True`.
- System deps (see CI): `libgdal-dev gettext libmagic1`; Node 20 + global `less`; `npm install`.
- Tests need running services: Postgres/PostGIS, Redis, Elasticsearch 7.17.9, and a
  **mailroom** at `MAILROOM_URL` (default `http://localhost:8090`) against the same DB.

## Commands
- Full suite: `tox -e py312` or `.venv/bin/coverage run manage.py test --keepdb --noinput`.
- Single test: `.venv/bin/python manage.py test temba.<app>.tests.<Class>.<method>`.
- Lint/format: `tox -e lint` / `pre-commit run --all-files`
  (django-upgrade 4.2, pyupgrade py312, **flynt**, ruff, ruff-format).
- Repo gate: `.venv/bin/python code_check.py` — runs `makemigrations`, ruff `--fix`+format,
  then fails if `git diff temba locale` is non-empty.
- Migrations: `manage.py makemigrations`; CI enforces `makemigrations --check --dry-run`.
  Squashed migrations are `NNNN_squashed.py`.

## Gotchas (things that bite)
- Any code change must leave `git diff temba locale` clean: run `makemigrations` and commit
  generated migrations/locale.
- Use `.venv/bin/python` / `uv run`, not bare `python`/`pip`. Upstream docs say Poetry;
  this fork uses **uv** (`[dependency-groups]`, `uv.lock`, `uv_build`).
- Root `mailroom` and `rp-indexer` are committed build artifacts (mailroom = surveyor-capable
  Jan-2023 build). CI downloads its own pinned versions. Don't treat the root binaries as
  source of truth or casually replace them.
- Flow/broadcast/campaign tests hit the mailroom HTTP client (`temba/mailroom/client.py`);
  without a running mailroom those tests fail.
- Settings module: default `temba.settings`; tests/CI/tox use `temba.settings_ci`, which runs
  against a DB literally named `temba` so mailroom can share it.
- Static compression uses `--extension=".haml"`. `static/bower` is vendored (excluded from
  ruff); `node_modules/` is not app source.
- Surveyor path depends on Mailroom `POST /mr/surveyor/submit` and spec <= 13.x; don't remove
  or bump past these without rebuilding the Surveyor app.

## Conventions
- License AGPL-3.0; preserve upstream mergeability — avoid repo-wide restructures.
- Keep gettext msgids static: `_("... %(x)s") % {...}`, never f-strings inside `_()`
  (flynt runs repo-wide but must not change msgids).
