#!/usr/bin/env python3
"""Save record details and covers for the record log, so builds need no network.

Reads data/records.toml and brings the saved files in line with it:

  data/musicbrainz.json   title, artists and year per MusicBrainz release group
  assets/covers/          one cover image per record

Records that are already saved are skipped, new ones are downloaded, and saved
files for records no longer in the log are deleted. Commit the saved files with
your site. Run from the site root, after editing data/records.toml:

  python3 themes/hugo-tufte/scripts/sync-records.py            # sync
  python3 themes/hugo-tufte/scripts/sync-records.py --refresh  # re-download everything

Needs Python 3.11+ and nothing else.
"""

import argparse
import hashlib
import json
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:
    sys.exit("sync-records: needs Python 3.11 or newer (for tomllib)")

USER_AGENT = "hugo-tufte-sync-records/1.0 (https://github.com/Raian256/hugo-tufte)"
MUSICBRAINZ = "https://musicbrainz.org/ws/2/release-group/{}?inc=artist-credits&fmt=json"
COVER_ART = "https://coverartarchive.org/release-group/{}/front-250"
MBID = re.compile(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}")
EXTENSIONS = {"image/jpeg": ".jpg", "image/png": ".png", "image/webp": ".webp", "image/gif": ".gif"}


def mbid_of(entry):
    """The release-group ID in `mbid`, which may be a bare ID or a musicbrainz.org URL."""
    match = MBID.search(entry.get("mbid", ""))
    return match.group(0) if match else None


def cover_key(entry, mbid):
    """File name (without extension) of an entry's cover: the MBID, or a hash of the `cover` URL.

    Must match layouts/partials/records.html.
    """
    if entry.get("cover"):
        return hashlib.sha1(entry["cover"].encode()).hexdigest()[:16]
    return mbid


class Fetcher:
    """HTTP GET with a User-Agent, spacing requests to each host as MusicBrainz asks."""

    def __init__(self):
        self.last = {}

    def get(self, url, gap):
        host = url.split("/")[2]
        wait = self.last.get(host, 0) + gap - time.monotonic()
        if wait > 0:
            time.sleep(wait)
        self.last[host] = time.monotonic()
        request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        with urllib.request.urlopen(request, timeout=30) as response:
            return response.read(), response.headers.get_content_type()


def fetch_details(fetcher, mbid):
    body, _ = fetcher.get(MUSICBRAINZ.format(mbid), gap=1.1)
    data = json.loads(body)
    # One name per credit rather than MusicBrainz's single joined string, so a
    # record with a composer, an orchestra, a conductor and a soloist is filed
    # under each of them.
    artists = [c["name"] for c in data.get("artist-credit", [])]
    return {
        "title": data["title"],
        "artists": artists,
        "year": (data.get("first-release-date") or "")[:4],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--site", default=".", help="site root (default: current directory)")
    parser.add_argument("--refresh", action="store_true", help="re-download everything")
    args = parser.parse_args()

    site = Path(args.site)
    log_file = site / "data" / "records.toml"
    saved_file = site / "data" / "musicbrainz.json"
    covers = site / "assets" / "covers"
    if not log_file.exists():
        sys.exit(f"sync-records: {log_file} not found; run from the site root or pass --site")

    entries = tomllib.loads(log_file.read_text()).get("records", [])
    saved = {} if args.refresh or not saved_file.exists() else json.loads(saved_file.read_text())
    covers.mkdir(parents=True, exist_ok=True)
    existing_covers = {p.stem: p for p in covers.iterdir() if p.is_file()}

    fetcher = Fetcher()
    wanted_details, wanted_covers = set(), set()
    downloaded, problems = 0, 0

    for entry in entries:
        mbid = mbid_of(entry)
        name = entry.get("title") or entry.get("mbid") or "an entry"
        if entry.get("mbid") and not mbid:
            print(f"  ! {name}: `mbid` doesn't contain a MusicBrainz ID")
            problems += 1

        # Details, unless the entry spells them all out.
        if mbid and not all(entry.get(k) for k in ("title", "artists", "year")):
            wanted_details.add(mbid)
            if mbid not in saved:
                try:
                    saved[mbid] = fetch_details(fetcher, mbid)
                    downloaded += 1
                    print(f"  + {', '.join(saved[mbid]['artists'])}, {saved[mbid]['title']}")
                except (urllib.error.URLError, KeyError, ValueError) as error:
                    print(f"  ! {name}: couldn't get details from MusicBrainz ({error}); is it a release-group ID?")
                    problems += 1
                    continue

        # Cover: from `cover` if given, else the Cover Art Archive.
        key = cover_key(entry, mbid)
        if not key:
            continue
        wanted_covers.add(key)
        if key in existing_covers and not args.refresh:
            continue
        url = entry.get("cover") or COVER_ART.format(mbid)
        try:
            image, content_type = fetcher.get(url, gap=0.5)
            extension = EXTENSIONS.get(content_type)
            if not extension:
                raise ValueError(f"not an image ({content_type})")
            for old in covers.glob(f"{key}.*"):
                old.unlink()
            (covers / f"{key}{extension}").write_bytes(image)
            downloaded += 1
        except (urllib.error.URLError, ValueError) as error:
            print(f"  ! {name}: no cover saved ({error})")
            problems += 1

    removed = 0
    for mbid in set(saved) - wanted_details:
        del saved[mbid]
        removed += 1
    for key, path in existing_covers.items():
        if key not in wanted_covers:
            path.unlink()
            removed += 1

    saved_file.write_text(json.dumps(dict(sorted(saved.items())), indent=2, ensure_ascii=False) + "\n")
    print(f"sync-records: {len(entries)} records, {downloaded} files downloaded, {removed} removed, {problems} problems")


if __name__ == "__main__":
    main()
