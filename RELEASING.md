# Releasing emailtrail

## PyPI account setup

Log in to [PyPI](https://pypi.org/account/login/) as the project's owner
(`akshayKMR`). Verify your email and set up two-factor authentication if prompted.
If password reset is blocked by an unverified email, use
[PyPI account recovery](https://pypi.org/help/#account-recovery).

In [account settings](https://pypi.org/manage/account/#api-tokens), create an API
token scoped to `emailtrail`. Keep the whole token, including the `pypi-` prefix.
You will paste it into the script's hidden prompt, not into a file or chat.

## Release

1. Pick an unused version, update `pyproject.toml`, and run `uv lock`.
   The version is still `0.4.0`, which is already published; change it before uploading.
2. Commit the release changes and check CI.
3. Rehearse from the repository root (no upload):

   ```sh
   ./scripts/release.sh
   ```

4. Publish when ready:

   ```sh
   ./scripts/release.sh --publish
   ```

The script checks lint, formatting, tests, and package metadata, then prompts for
your API token with input hidden. It also accepts `UV_PUBLISH_TOKEN` from the
environment. No GitHub publishing setup is needed.

Each run keeps its wheel and source archive in a fresh `dist/release.*` directory.
Only those two files are uploaded. Matching files already on PyPI are skipped so
an interrupted upload can be retried; existing files cannot be overwritten.
The script does not change versions, commit, tag, or push.

After publishing, check the release on PyPI. From outside this repository, replace
`VERSION` below with the version you published and verify installation:

```sh
uv run --no-project --with 'emailtrail==VERSION' python -c "import emailtrail; print(emailtrail.analyse_headers(''))"
```
