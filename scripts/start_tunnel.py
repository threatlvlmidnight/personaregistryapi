from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from urllib.error import URLError
from urllib.request import urlopen


TRY_CLOUDFLARE_PATTERN = re.compile(r"https://[a-zA-Z0-9.-]+\.trycloudflare\.com")


def resolve_cloudflared_path(explicit_path: str | None = None) -> str | None:
    candidates: list[str] = []

    if explicit_path:
        candidates.append(explicit_path)

    env_path = os.getenv("CLOUDFLARED_PATH")
    if env_path:
        candidates.append(env_path)

    which_path = shutil.which("cloudflared")
    if which_path:
        candidates.append(which_path)

    candidates.extend(
        [
            r"C:\Program Files\cloudflared\cloudflared.exe",
            r"C:\Program Files (x86)\cloudflared\cloudflared.exe",
        ]
    )

    for candidate in candidates:
        if candidate and Path(candidate).exists():
            return str(Path(candidate))

    return None


def check_local_api(url: str) -> bool:
    try:
        with urlopen(url, timeout=2) as response:
            return 200 <= response.status < 500
    except URLError:
        return False


def run_tunnel(cloudflared_path: str, target_url: str) -> int:
    command = [cloudflared_path, "tunnel", "--url", target_url]
    print(f"Starting tunnel: {' '.join(command)}")

    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
    )

    found_public_url = False
    try:
        if process.stdout is None:
            return process.wait()

        for line in process.stdout:
            print(line.rstrip())
            if not found_public_url:
                match = TRY_CLOUDFLARE_PATTERN.search(line)
                if match:
                    found_public_url = True
                    print(f"\nPublic URL: {match.group(0)}")
                    print("Share this URL with Alex. Press Ctrl+C to stop the tunnel.\n")

        return process.wait()
    except KeyboardInterrupt:
        print("\nStopping tunnel...")
        process.terminate()
        return process.wait(timeout=10)


def main() -> int:
    parser = argparse.ArgumentParser(description="Start a Cloudflare tunnel to a local API")
    parser.add_argument("--url", default="http://127.0.0.1:8000", help="Local URL to expose")
    parser.add_argument("--cloudflared-path", default=None, help="Optional explicit path to cloudflared executable")
    parser.add_argument(
        "--skip-health-check",
        action="store_true",
        help="Skip local URL health check before starting tunnel",
    )
    args = parser.parse_args()

    cloudflared_path = resolve_cloudflared_path(args.cloudflared_path)
    if not cloudflared_path:
        print("Could not find cloudflared executable.")
        print("Install with: winget install --id Cloudflare.cloudflared -e")
        print("Or pass --cloudflared-path 'C:\\Path\\To\\cloudflared.exe'")
        return 1

    if not args.skip_health_check and not check_local_api(args.url):
        print(f"Local URL is not reachable: {args.url}")
        print("Start your API first, or run again with --skip-health-check.")
        return 1

    return run_tunnel(cloudflared_path, args.url)


if __name__ == "__main__":
    raise SystemExit(main())
