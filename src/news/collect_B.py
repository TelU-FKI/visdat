#!/usr/bin/env python3
"""Collect Indonesian IHSG headlines for shard B from Google News RSS."""

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


START = date(2026, 4, 1)
END_EXCLUSIVE = date(2026, 7, 1)
QUERIES = (
    "IHSG",
    "IHSG ditutup",
    "indeks harga saham gabungan",
    "IHSG hari ini saham",
)
BASE_URL = "https://news.google.com/rss/search?"
OUTPUT = Path(__file__).resolve().parents[2] / "data/news/shard_B.csv"
WIB = ZoneInfo("Asia/Jakarta")


def windows():
    start = START
    while start < END_EXCLUSIVE:
        end = min(start + timedelta(days=7), END_EXCLUSIVE)
        yield start, end
        start = end


def fetch(url):
    request = urllib.request.Request(
        url, headers={"User-Agent": "Mozilla/5.0 (compatible; IHSGNewsCollector/1.0)"}
    )
    for attempt in range(3):
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                return ET.fromstring(response.read())
        except (urllib.error.URLError, TimeoutError, ET.ParseError):
            if attempt == 2:
                raise
            time.sleep(2 * (attempt + 1))


def main():
    records = {}
    first_request = True
    for window_start, window_end in windows():
        for query in QUERIES:
            if not first_request:
                time.sleep(1.5)
            first_request = False
            params = {
                "q": f"{query} after:{window_start.isoformat()} before:{window_end.isoformat()}",
                "hl": "id",
                "gl": "ID",
                "ceid": "ID:id",
            }
            root = fetch(BASE_URL + urllib.parse.urlencode(params))
            for item in root.findall("./channel/item"):
                title_node = item.find("title")
                pubdate_node = item.find("pubDate")
                if title_node is None or pubdate_node is None or not title_node.text:
                    continue
                published = email.utils.parsedate_to_datetime(pubdate_node.text)
                if published.tzinfo is None:
                    published = published.replace(tzinfo=ZoneInfo("UTC"))
                published = published.astimezone(WIB)
                if not (window_start <= published.date() < window_end):
                    continue
                title = " ".join(title_node.text.split())
                source_node = item.find("source")
                source = " ".join((source_node.text or "").split()) if source_node is not None else ""
                if source and title.endswith(f" - {source}"):
                    title = title[: -(len(source) + 3)].rstrip()
                lowered = title.casefold()
                if "ihsg" not in lowered and "indeks harga saham gabungan" not in lowered:
                    continue
                normalized = " ".join(title.casefold().split())
                link_node = item.find("link")
                records.setdefault(
                    normalized,
                    {
                        "tanggal": published.date().isoformat(),
                        "judul": title,
                        "sumber": source,
                        "url": link_node.text if link_node is not None and link_node.text else "",
                        "query": query,
                    },
                )

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    fields = ["tanggal", "judul", "sumber", "url", "query"]
    with OUTPUT.open("w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fields)
        writer.writeheader()
        writer.writerows(sorted(records.values(), key=lambda row: (row["tanggal"], row["judul"].casefold())))
    print(f"Wrote {len(records)} headlines to {OUTPUT}")


if __name__ == "__main__":
    main()
