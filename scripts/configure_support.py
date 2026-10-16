#!/usr/bin/env python3
"""Configure Stretch's optional donation links from one real profile URL."""
import argparse
import json
import plistlib
import re
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parent.parent
START = "<!-- support:start -->"
END = "<!-- support:end -->"


def configure(profile_url: str, root: Path = ROOT) -> None:
    url = urlsplit(profile_url)
    username = url.path.strip("/")
    if (url.scheme != "https" or url.netloc.lower() not in
            {"buymeacoffee.com", "www.buymeacoffee.com"} or
            url.query or url.fragment or
            not re.fullmatch(r"[A-Za-z0-9_.-]+", username)):
        raise ValueError("Use the full HTTPS Buy Me a Coffee profile URL, with one profile name and no query or fragment.")
    canonical = f"https://www.buymeacoffee.com/{username}"
    readme_path = root / "README.md"
    readme = readme_path.read_text()
    if readme.count(START) != 1 or readme.count(END) != 1:
        raise ValueError("README must contain exactly one support marker pair.")
    before, middle = readme.split(START, 1)
    _, after = middle.split(END, 1)
    plist_path = root / "mac-app/Stretch.app/Contents/Info.plist"
    info = plistlib.loads(plist_path.read_bytes())
    info["StretchSupportURL"] = canonical
    funding = root / ".github/FUNDING.yml"
    funding.parent.mkdir(parents=True, exist_ok=True)
    funding.write_text("buy_me_a_coffee: " + json.dumps(username) + "\n")
    readme_path.write_text(before + START + "\nEnjoying Stretch? [Buy me a coffee](" + canonical + ") to help it grow. Donations are completely optional.\n" + END + after)
    plist_path.write_bytes(plistlib.dumps(info))
    print("Configured GitHub, README and app support links:", canonical)
    print("Rebuild the app, check the destination, then commit and push.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("profile_url", help="Your real Buy Me a Coffee HTTPS profile URL")
    args = parser.parse_args()
    try:
        configure(args.profile_url)
    except ValueError as error:
        parser.error(str(error))
