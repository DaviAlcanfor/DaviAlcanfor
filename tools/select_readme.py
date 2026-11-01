"""Pick the live profile README: copy readmes/<name>/README.md to the root and mirror its assets.

GitHub only renders README.md at the root, so the chosen variant is copied there. Each variant
keeps its own assets/, which are mirrored into the root assets/ folder.

    python tools/select_readme.py           # list the variants, marking the active one
    python tools/select_readme.py terminal  # make it the profile README
"""
import shutil
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
READMES = REPO / "readmes"
ROOT_README = REPO / "README.md"
ROOT_ASSETS = REPO / "assets"


def variants():
    """Folders under readmes/ that hold a README.md. Drafts have none, so they are skipped."""
    return sorted(p.name for p in READMES.iterdir() if (p / "README.md").is_file())


def active():
    if not ROOT_README.is_file():
        return None
    current = ROOT_README.read_bytes()
    return next((v for v in variants() if (READMES / v / "README.md").read_bytes() == current), None)


def select(name):
    src = READMES / name
    shutil.copyfile(src / "README.md", ROOT_README)
    shutil.rmtree(ROOT_ASSETS, ignore_errors=True)
    shutil.copytree(src / "assets", ROOT_ASSETS)


def main(argv):
    if len(argv) < 2:
        current = active()
        for name in variants():
            print(f"{'*' if name == current else ' '} {name}")
        return
    name = argv[1]
    if name not in variants():
        sys.exit(f"unknown variant {name!r}; choose one of: {', '.join(variants())}")
    select(name)
    print(f"README.md <- readmes/{name}/README.md, assets/ <- readmes/{name}/assets/")


if __name__ == "__main__":
    main(sys.argv)
