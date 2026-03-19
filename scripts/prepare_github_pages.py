from __future__ import annotations

from pathlib import Path


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    source = root / "web" / "index.html"
    target_dir = root / "docs"
    target = target_dir / "index.html"
    nojekyll = target_dir / ".nojekyll"

    if not source.exists():
        raise FileNotFoundError(f"Missing source page: {source}")

    target_dir.mkdir(parents=True, exist_ok=True)
    target.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")
    nojekyll.write_text("", encoding="utf-8")

    print("Prepared GitHub Pages files:")
    print(f"- {target}")
    print(f"- {nojekyll}")
    print("Next: commit and push, then enable GitHub Pages from branch main / folder docs.")


if __name__ == "__main__":
    main()
