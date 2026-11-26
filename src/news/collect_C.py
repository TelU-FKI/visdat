#!/usr/bin/env python3
"""Collect the July–November 2026 IHSG news shard from Google News RSS."""

import csv
import email.utils
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import date, datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo


START = date(2026, 7, 1)
END_EXCLUSIVE = date(2026, 11, 10)
QUERIES = ("IHSG", "IHSG ditutup", "indeks harga saham gabungan", "IHSG hari ini saham")
BASE_URL = "https://news.google.com/rss/search"
OUTPUT = Path(__file__).resolve().parents[2] / "data/news/shard_C.csv"
WIB = ZoneInfo("Asia/Jakarta")


def windows():
    start = START
    while start < END_EXCLUSIVE:
        end = min(start + timedelta(days=7), END_EXCLUSIVE)
        yield start, end
        start = end


def fetch(query, start, end):
    params = {
        "q": f'{query} after:{start.isoformat()} before:{end.isoformat()}',
        "hl": "id", "gl": "ID", "ceid": "ID:id",
    }
    request = urllib.request.Request(
        f"{BASE_URL}?{urllib.parse.urlencode(params)}",
        headers={"User-Agent": "Mozilla/5.0 (compatible; IHSGNewsCollector/1.0)"},
    )
    last_error = None
    for attempt in range(3):
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                return ET.fromstring(response.read())
        except (urllib.error.URLError, TimeoutError, ET.ParseError) as exc:
            last_error = exc
            if attempt < 2:
                time.sleep(2)
    raise RuntimeError(f"RSS request failed for {query!r}, {start}–{end}: {last_error}")


def normalize_title(title):
    return " ".join(title.lower().split())


def main():
    rows = {}
    previous_request = 0.0
    for start, end in windows():
        for query in QUERIES:
            wait = 1.5 - (time.monotonic() - previous_request)
            if previous_request and wait > 0:
                time.sleep(wait)
            root = fetch(query, start, end)
            previous_request = time.monotonic()
            for item in root.findall("./channel/item"):
                title_node = item.find("title")
                pub_node = item.find("pubDate")
                if title_node is None or pub_node is None or not title_node.text:
                    continue
                title_with_source = title_node.text.strip()
                # Google News titles conventionally end in " - Source".
                title = title_with_source.rsplit(" - ", 1)[0].strip() if " - " in title_with_source else title_with_source
                lowered = title.lower()
                if "ihsg" not in lowered and "indeks harga saham gabungan" not in lowered:
                    continue
                try:
                    published = email.utils.parsedate_to_datetime(pub_node.text)
                    if published.tzinfo is None:
                        published = published.replace(tzinfo=ZoneInfo("UTC"))
                    published = published.astimezone(WIB)
                except (TypeError, ValueError, OverflowError):
                    continue
                if not (START <= published.date() < END_EXCLUSIVE):
                    continue
                source_node = item.find("source")
                source = source_node.text.strip() if source_node is not None and source_node.text else ""
                link_node = item.find("link")
                link = link_node.text.strip() if link_node is not None and link_node.text else ""
                key = normalize_title(title)
                rows.setdefault(key, {
                    "tanggal": published.date().isoformat(), "judul": title,
                    "sumber": source, "url": link, "query": query,
                })

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    fields = ("tanggal", "judul", "sumber", "url", "query")
    with OUTPUT.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(sorted(rows.values(), key=lambda row: (row["tanggal"], row["judul"].lower())))
    print(f"Wrote {len(rows)} rows to {OUTPUT}")


if __name__ == "__main__":
    main()
