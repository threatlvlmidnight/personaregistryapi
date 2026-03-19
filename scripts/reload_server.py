from __future__ import annotations

from app.main import write_reload_trigger


def main() -> None:
    write_reload_trigger()
    print("Reload requested")


if __name__ == "__main__":
    main()