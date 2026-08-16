#!/usr/bin/env python3
"""Notify IndexNow-compatible search engines about changed site URLs."""

from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path
from urllib.parse import urlparse


DEFAULT_ENDPOINT = "https://api.indexnow.org/indexnow"
DEFAULT_KEY_FILE = "d5ab72c3785258477f77b42bfe4201cb.txt"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Submit changed jftagro.com URLs to IndexNow."
    )
    parser.add_argument("urls", nargs="+", help="Absolute URLs that changed")
    parser.add_argument("--host", default="jftagro.com")
    parser.add_argument("--key-file", default=DEFAULT_KEY_FILE)
    parser.add_argument("--endpoint", default=DEFAULT_ENDPOINT)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    project_root = Path(__file__).resolve().parent.parent
    key_path = project_root / args.key_file
    key = key_path.read_text(encoding="utf-8").strip()

    if not re.fullmatch(r"[A-Za-z0-9-]{8,128}", key):
        raise ValueError("IndexNow key must be 8-128 letters, numbers, or dashes")
    if len(args.urls) > 10_000:
        raise ValueError("IndexNow accepts at most 10,000 URLs per request")

    for url in args.urls:
        parsed = urlparse(url)
        if parsed.scheme not in {"http", "https"} or parsed.hostname != args.host:
            raise ValueError(f"URL does not belong to {args.host}: {url}")

    payload = {
        "host": args.host,
        "key": key,
        "keyLocation": f"https://{args.host}/{key_path.name}",
        "urlList": args.urls,
    }
    request = urllib.request.Request(
        args.endpoint,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json; charset=utf-8"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            print(f"IndexNow accepted {len(args.urls)} URL(s): HTTP {response.status}")
            return 0 if response.status in {200, 202} else 1
    except urllib.error.HTTPError as error:
        detail = error.read().decode("utf-8", errors="replace").strip()
        print(f"IndexNow rejected the request: HTTP {error.code} {detail}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
