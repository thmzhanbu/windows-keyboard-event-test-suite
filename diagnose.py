"""Preflight checks; never imports pynput or starts a keyboard listener."""

import argparse
import importlib
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parent


def check_packages(live=False):
    ok = True
    for package in (["pytest", "pynput"] if live else ["pytest"]):
        try:
            print(f"[OK] Package: {package} {version(package)}")
        except PackageNotFoundError:
            print(f"[FAIL] Missing {package}: python -m pip install -r requirements.txt")
            ok = False
    return ok


def check_logs(path):
    try:
        path.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryFile(mode="w+", encoding="utf-8", dir=path) as probe:
            probe.write("probe")
            probe.flush()
        print(f"[OK] Log directory is writable: {path}")
        return True
    except OSError as exc:
        print(f"[FAIL] Log directory: {exc}")
        return False


def check_src_imports():
    ok = True
    for name in ("src.keylogger", "src.log_handler"):
        try:
            importlib.import_module(name)
            print(f"[OK] Module: {name}")
        except Exception as exc:
            print(f"[FAIL] Module {name}: {exc}")
            ok = False
    return ok


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--live", action="store_true",
                        help="Also require Windows and the pynput distribution")
    args = parser.parse_args(argv)
    python_ok = sys.version_info >= (3, 9)
    print("=== Keylogger Test Suite Diagnostics ===")
    print(f"[{'OK' if python_ok else 'FAIL'}] Python: {sys.version.split()[0]}")
    platform_ok = not args.live or sys.platform == "win32"
    if args.live:
        print(f"[{'OK' if platform_ok else 'FAIL'}] Live capture requires Windows")
    else:
        print("[INFO] Simulated tests only; live keyboard capture is not checked.")
    results = [python_ok, platform_ok, check_packages(args.live),
               check_logs(ROOT / "logs"), check_src_imports()]
    if all(results):
        print("All checks passed. Run: python -m pytest tests/ -v")
        return 0
    print("One or more checks failed. Fix the issues above.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
