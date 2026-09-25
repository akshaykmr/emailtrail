# Releasing emailtrail

## One-time setup

In the existing emailtrail project's PyPI publishing settings, add a GitHub
Trusted Publisher with these exact values:

- Owner: `akshaykmr`
- Repository: `emailtrail`
- Workflow: `publish.yml`
- Environment: `pypi`

Create the `pypi` environment in the GitHub repository settings. Consider requiring
a maintainer's approval for deployments to this environment. No PyPI API token
is needed for this workflow.

## Release checklist

1. Set the version in `pyproject.toml`, run `uv lock`, and date the matching entry
   in `CHANGELOG.md`.
2. Run `uv sync --locked`, `make lint`, `make test`, and `make build`.
3. Merge the release commit and ensure GitHub's full OS/Python matrix is green.
4. Create a GitHub release targeting that commit, with the tag `v<version>`
   (for this release, `v0.5.0`), and copy the changelog entry into its notes.
5. Publishing the GitHub release triggers `publish.yml`. It reruns CI, validates
   the tag against package metadata, builds distributions, and uploads them to
   PyPI using Trusted Publishing. Approve the environment deployment if enabled.
6. Check the PyPI description and install the published version in a fresh
   environment: `uv run --no-project --with emailtrail==0.5.0 python -c
   "import emailtrail; print(emailtrail.analyse_headers(''))"` (run outside the
   repository so local source cannot mask the installed package).

PyPI releases are immutable. If an upload has succeeded, use a new version for
subsequent fixes. `uv.lock` pins development/CI dependencies; users installing
the library receive the compatible dependency ranges in `pyproject.toml`.
