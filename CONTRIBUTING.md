# Contributing to RapidPro

Contributions to the RapidPro projects are highly appreciated! 

We accept contributions in the form of:
 * Bug reports 
 * Pull requests for code changes
 * Documentation updates

All non-trivial pull requests, especially those with functional changes should first open a ticket to discuss approach 
and likelihood of inclusion in the project.

Note that all pull requests must:

 * Pass all unit tests
 * Maintain 100% unit test coverage (without new no-covers)
 * Pass the code quality checks (ruff etc)

Install the git hooks with `pre-commit install` so the checks run automatically on commit. You can also run
`pre-commit run --all-files` to check the whole repository, or `code_check.py` to additionally check for missing
migrations.

## Running tests locally

The test suite uses the same settings as CI (`temba.settings_ci`) and expects the following services to be running:

 * PostgreSQL with PostGIS on `localhost:5432` with database/user/password `temba`/`temba`/`temba`
 * Redis on `localhost:6379`
 * Node dependencies installed with `npm install` (provides the component templates)
 * Mailroom on `localhost:8090` (only needed by some tests)
 * Elasticsearch on `localhost:9200` (only needed by the search tests)

Create the local database with:

```
psql -d postgres -c "CREATE ROLE temba WITH LOGIN PASSWORD 'temba' SUPERUSER;"
psql -d postgres -c "CREATE DATABASE temba OWNER temba;"
psql -d temba -c "CREATE EXTENSION IF NOT EXISTS postgis;"
```

Then install the Python environment and run the suite with tox:

```
uv sync
uvx --with tox-uv tox                          # whole suite plus coverage
uvx --with tox-uv tox -e py312 -- temba.contacts   # a single app/module
uvx --with tox-uv tox -e lint                  # ruff and the other pre-commit hooks
```

Any arguments after `--` are passed through to `manage.py test`.

RapidPro is licensed under the AGPL-3.0 and your contributions will be licensed in the same way. Note that contributing 
does not change your rights to use your own Contributions for any other purpose.
