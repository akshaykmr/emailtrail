#!/usr/bin/env bash
# Build/check by default. Upload only when explicitly called with --publish.
set +x
set -euo pipefail

usage() {
    printf '%s\n' \
        'Usage: ./scripts/release.sh [--publish]' \
        '  No arguments: lint, test, build, and validate (no upload).' \
        '  --publish:    also upload to PyPI, prompting for an API token.' \
        '               Alternatively, set UV_PUBLISH_TOKEN in the environment.'
}

publish=false
case "${1:-}" in
    '') ;;
    --publish) publish=true ;;
    -h|--help) usage; exit 0 ;;
    *) usage >&2; exit 2 ;;
esac
if (( $# > 1 )); then
    usage >&2
    exit 2
fi

command -v uv >/dev/null || {
    printf '%s\n' 'Install uv first: https://docs.astral.sh/uv/getting-started/installation/' >&2
    exit 1
}
repo_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
cd "$repo_dir"

uv sync --locked
version=$(uv version --short)
printf '\nChecking emailtrail %s\n' "$version"
uv run --locked ruff check .
uv run --locked ruff format --check .
uv run --locked pytest

# A fresh directory prevents old releases in dist/ from being uploaded.
mkdir -p dist
release_dir=$(mktemp -d "$repo_dir/dist/release.XXXXXX")
uv build --out-dir "$release_dir"
artifacts=("$release_dir/emailtrail-$version-py3-none-any.whl" "$release_dir/emailtrail-$version.tar.gz")
uv run --locked twine check --strict "${artifacts[@]}"

printf '\nValidated distributions: %s\n' "$release_dir"
if [[ "$publish" == false ]]; then
    printf '%s\n' 'Nothing uploaded. To publish, run ./scripts/release.sh --publish'
    exit 0
fi

if [[ -z "${UV_PUBLISH_TOKEN:-}" ]]; then
    if [[ ! -t 0 ]]; then
        printf '%s\n' 'Publishing needs UV_PUBLISH_TOKEN or an interactive terminal for the token prompt.' >&2
        exit 1
    fi
    read -r -s -p 'PyPI API token (hidden): ' UV_PUBLISH_TOKEN
    printf '\n'
fi
if [[ -z "$UV_PUBLISH_TOKEN" ]]; then
    printf '%s\n' 'No token supplied; nothing uploaded.' >&2
    exit 1
fi

# Pass the token through the environment, never a command-line argument.
# Always target production PyPI, regardless of ambient uv index settings.
(
    unset UV_PUBLISH_INDEX UV_PUBLISH_USERNAME UV_PUBLISH_PASSWORD
    export UV_PUBLISH_TOKEN
    uv publish --no-config --trusted-publishing never --keyring-provider disabled \
        --publish-url https://upload.pypi.org/legacy/ \
        --check-url https://pypi.org/simple/ "${artifacts[@]}"
)
printf '\nPublished: https://pypi.org/project/emailtrail/%s/\n' "$version"
