# CI / Release Workflow

## How to trigger a release build

```bash
git tag v20250420        # date-based version, matching the package's versioning scheme
git push origin v20250420
```

This triggers `.github/workflows/wheels.yml`, which:
1. Builds wheels for **cp311, cp312, cp313, cp314** across:
   - Linux x86_64 + aarch64
   - macOS Intel (x86_64) + Apple Silicon (arm64)
   - Windows AMD64
2. Publishes all wheels to a **GitHub Release** with auto-generated notes.

## Version string

The version lives in `triangle/version.py`. Update it before tagging:

```python
__version__ = '20250420'
```

## Local build

```bash
pip install cibuildwheel
cibuildwheel --platform linux   # requires Docker
```

## Dependencies

- [`pypa/cibuildwheel`](https://github.com/pypa/cibuildwheel) — builds the wheels
- [`docker/setup-qemu-action`](https://github.com/docker/setup-qemu-action) — enables Linux aarch64 cross-compilation
- C source: [`drufat/triangle-c`](https://github.com/drufat/triangle-c) submodule in `c/`
