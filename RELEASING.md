# Releasing emailtrail

## Publish from your computer (Bash + uv)

1. Log in to [PyPI](https://pypi.org/account/login/). The existing project owner
   is `akshayKMR`. Use password recovery if needed; PyPI also requires two-factor
   authentication. Check that `emailtrail` appears under your projects.
2. In [account settings](https://pypi.org/manage/account/#api-tokens), create an
   API token scoped to the `emailtrail` project. Copy the whole token, including
   its `pypi-` prefix. This is used for uploading, not your account password.
3. Set the version in `pyproject.toml`, run `uv lock`, and date its changelog
   entry. Commit the release changes and check the GitHub CI results when available.
4. From the repository, run a rehearsal (no upload):

   ```sh
   ./scripts/release.sh
   ```

5. When ready to publish:

   ```sh
   ./scripts/release.sh --publish
   ```

   The script reruns lint, formatting checks, tests, builds, and package metadata
   checks, then prompts for your API token with input hidden. Paste the token
   into that local prompt, not into chat or a tracked file. It is not saved.
   For automation, the script also accepts `UV_PUBLISH_TOKEN` from the environment.

Each run keeps its distributions in a fresh `dist/release.*` directory and only
uploads that run's wheel and source archive. Matching files already on PyPI are
skipped, allowing a retry if one of the two uploads failed. Different content
cannot overwrite an existing file. No GitHub access or Trusted Publisher setup
is needed for this local upload. The script does not commit, tag, or push changes.

After uploading, verify the version on PyPI and install it outside this repository:

```sh
uv run --no-project --with emailtrail==0.5.0 python -c "import emailtrail; print(emailtrail.analyse_headers(''))"
```

See [PyPI's API token help](https://pypi.org/help/#apitoken) for account setup.

## Alternative: publish through GitHub Actions

### One-time setup

In the existing emailtrail project's PyPI publishing settings, add a GitHub
Trusted Publisher with these exact values:

- Owner: `akshaykmr`
- Repository: `emailtrail`
- Workflow: `publish.yml`
- Environment: `pypi`

Create the `pypi` environment in the GitHub repository settings. Consider requiring
a maintainer's approval for deployments to this environment. No PyPI API token
is needed for this workflow.

### Release checklist

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

Choose either the local upload or the GitHub workflow for a version. If you
already uploaded locally, publishing a GitHub release would also trigger the
workflow; disable that workflow before doing so to avoid a duplicate upload.

PyPI releases are immutable. If an upload has succeeded, use a new version for
subsequent fixes. `uv.lock` pins development/CI dependencies; users installing
the library receive the compatible dependency ranges in `pyproject.toml`.
