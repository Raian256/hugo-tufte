#!/usr/bin/env python3
"""Save your Letterboxd diary and posters, so builds need no network.

Reads your public Letterboxd RSS feed and updates:

  data/letterboxd.json    your latest diary entries, as in the feed (up to 50)
  assets/posters/         one poster per film

The saved entries mirror the feed: new ones are added, edited ones updated,
and ones that dropped out of the feed removed. Posters are downloaded only for
films that don't have one yet, and deleted when no saved entry uses them. If
the feed can't be fetched, nothing changes.

Run from the site root, before building:

  python3 themes/hugo-tufte/scripts/sync-letterboxd.py
  python3 themes/hugo-tufte/scripts/sync-letterboxd.py --user someone   # override params.letterboxd

Needs Python 3.8+ and, unless --user is given, the `hugo` command (to read
params.letterboxd from your site config, whatever its format).
"""

import argparse
import json
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

USER_AGENT = "hugo-tufte-sync-letterboxd/1.0 (https://github.com/Raian256/hugo-tufte)"
FEED = "https://letterboxd.com/{}/rss/"
NS = {"letterboxd": "https://letterboxd.com", "tmdb": "https://themoviedb.org"}
EXTENSIONS = {"image/jpeg": ".jpg", "image/png": ".png", "image/webp": ".webp"}


def get(url):
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=30) as response:
        return response.read(), response.headers.get_content_type()


def username_from_config(site):
    try:
        out = subprocess.run(["hugo", "config", "--format", "json"], cwd=site,
                             capture_output=True, text=True, check=True).stdout
    except (OSError, subprocess.CalledProcessError) as error:
        sys.exit(f"sync-letterboxd: couldn't read the site config with `hugo config` ({error}); pass --user")
    user = json.loads(out).get("params", {}).get("letterboxd")
    if not user:
        sys.exit("sync-letterboxd: params.letterboxd isn't set; set it or pass --user")
    return user


def parse(feed):
    """Diary entries in the feed, as dicts ready to save, plus each entry's poster URL."""
    entries = []
    for item in ET.fromstring(feed).iter("item"):
        def field(name):
            return (item.findtext(name, namespaces=NS) or "").strip()

        title = field("letterboxd:filmTitle")
        if not title:  # lists and other non-diary items
            continue
        guid = field("guid")
        description = field("description")
        poster_url = re.search(r'<img src="([^"]+)"', description)
        review = ""
        if guid.startswith("letterboxd-review"):
            review = re.sub(r"<p>\s*<img[^>]*>\s*</p>", "", description).strip()
        link = field("link")
        slug = re.search(r"/film/([^/]+)/", link)
        rating = field("letterboxd:memberRating")
        entries.append(({
            "guid": guid,
            "title": title,
            "year": field("letterboxd:filmYear"),
            "link": link,
            "watched": field("letterboxd:watchedDate"),
            "rating": float(rating) if rating else 0,
            "liked": field("letterboxd:memberLike") == "Yes",
            "rewatch": field("letterboxd:rewatch") == "Yes",
            "review": review,
            "poster": field("tmdb:movieId") or (slug.group(1) if slug else ""),
        }, poster_url.group(1) if poster_url else None))
    return entries


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--site", default=".", help="site root (default: current directory)")
    parser.add_argument("--user", help="Letterboxd username (default: params.letterboxd)")
    args = parser.parse_args()

    site = Path(args.site)
    saved_file = site / "data" / "letterboxd.json"
    posters = site / "assets" / "posters"
    user = args.user or username_from_config(site)

    try:
        feed, _ = get(FEED.format(user))
    except urllib.error.URLError as error:
        sys.exit(f"sync-letterboxd: couldn't fetch the feed for {user!r} ({error}); nothing changed")

    previous = json.loads(saved_file.read_text())["entries"] if saved_file.exists() else []
    previous_guids = {entry["guid"] for entry in previous}
    posters.mkdir(parents=True, exist_ok=True)
    have_poster = {p.stem for p in posters.iterdir() if p.is_file()}

    entries, downloaded, problems = [], 0, 0
    for entry, poster_url in parse(feed):
        entries.append(entry)
        key = entry["poster"]
        if key and key not in have_poster and poster_url:
            try:
                time.sleep(0.5)
                image, content_type = get(poster_url)
                extension = EXTENSIONS.get(content_type)
                if not extension:
                    raise ValueError(f"not an image ({content_type})")
                (posters / f"{key}{extension}").write_bytes(image)
                have_poster.add(key)
                downloaded += 1
            except (urllib.error.URLError, ValueError) as error:
                print(f"  ! {entry['title']}: no poster saved ({error})")
                problems += 1

    entries.sort(key=lambda e: (e["watched"], e["guid"]), reverse=True)
    added = len({e["guid"] for e in entries} - previous_guids)
    dropped = len(previous_guids - {e["guid"] for e in entries})
    used = {e["poster"] for e in entries}
    removed = 0
    for path in posters.iterdir():
        if path.is_file() and path.stem not in used:
            path.unlink()
            removed += 1

    saved_file.parent.mkdir(parents=True, exist_ok=True)
    saved_file.write_text(json.dumps({"user": user, "entries": entries}, indent=2, ensure_ascii=False) + "\n")
    print(f"sync-letterboxd: {len(entries)} entries saved ({added} new, {dropped} dropped), "
          f"{downloaded} posters downloaded, {removed} removed, {problems} problems")


if __name__ == "__main__":
    main()
