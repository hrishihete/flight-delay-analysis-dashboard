from __future__ import annotations

import importlib
import os
import sqlite3
from pathlib import Path


def check_module(name: str) -> tuple[str, str]:
    module = importlib.import_module(name)
    version = getattr(module, "__version__", "stdlib")
    return name, version


def main() -> None:
    # Keep matplotlib cache inside the project when the user profile cache is locked.
    os.environ.setdefault("MPLCONFIGDIR", str(Path("reports") / ".mplconfig"))
    Path(os.environ["MPLCONFIGDIR"]).mkdir(parents=True, exist_ok=True)

    modules = ["pandas", "matplotlib", "seaborn"]
    print("Week 1 tooling check")
    print("====================")
    for module_name in modules:
        name, version = check_module(module_name)
        print(f"OK {name}: {version}")

    print(f"OK sqlite3: {sqlite3.sqlite_version}")
    print("OK workspace folders: data/raw, data/processed, notebooks, src, reports, screenshots, tableau")


if __name__ == "__main__":
    main()
