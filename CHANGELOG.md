# Changelog

## 0.5.0 (unreleased)

- Require Python 3.11 or newer; test Python 3.11–3.14 on Linux, macOS, and Windows.
  Python 3.9/3.10 users can continue using emailtrail 0.4.0.
- Accept string subclasses when parsing timestamps, thanks to Stephen0512 in
  [#7](https://github.com/akshaykmr/emailtrail/pull/7).
- Replace Poetry with uv, standard project metadata, and a committed lockfile.
- Update dependencies and replace the direct pytz dependency with Python's UTC
  timezone (dateparser may still depend on pytz).
- Replace Black/Flake8 with Ruff and add distribution validation to CI.
- Include the README, license, and project links in package metadata.
- Correct optional timestamp annotations and fix the dataset helper's use of Trail.
- Add a PyPI Trusted Publishing workflow and release instructions.
