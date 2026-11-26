#!/usr/bin/env python3
"""Collect Google News RSS headlines for IHSG, shard A (Jan–Mar 2026)."""

import csv
import email.utils
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import date, datetime, time as dt_time, timedelta, timezone
from pathlib import Path


START = date(2026, 1, 1)
END = date(2026, 4, 1)  # exclusive
QUERIES = (
    "IHSG",
    "IHSG ditutup",
    "indeks harga saham gabungan",
    "IHSG hari ini saham",
    "IHSG saham",
    "IHSG Indonesia",
    "pergerakan IHSG",
    "IHSG menguat",
    "IHSG melemah",
)
BASE_URL = "https://news.google.com/rss/search"
WIB = timezone(timedelta(hours=7))
USER_AGENT = "Mozilla/5.0 (compatible; IHSGNewsCollector/1.0)"
OUTPUT = Path(__file__).resolve().parents[2] / "data/news/shard_A.csv"
FIELDS = ("tanggal", "judul", "sumber", "url", "query")


def windows():
    start = START
    while start < END:
        stop = min(start + timedelta(days=7), END)
        yield start, stop
        start = stop


def get_feed(query, start, stop):
    full_query = f'{query} after:{start.isoformat()} before:{stop.isoformat()}'
    params = urllib.parse.urlencode({"q": full_query, "hl": "id", "gl": "ID", "ceid": "ID:id"})
    request = urllib.request.Request(
        f"{BASE_URL}?{params}", headers={"User-Agent": USER_AGENT}
    )
    for attempt in range(3):
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                return ET.fromstring(response.read())
        except (urllib.error.URLError, TimeoutError, ET.ParseError) as exc:
            if attempt == 2:
                print(f"Gagal mengambil {query!r} {start}: {exc}")
                return None
            time.sleep(2 * (attempt + 1))


def clean_title(title):
    title = " ".join((title or "").split())
    # Google News titles append the publisher after the final spaced dash.
    if " - " in title:
        title = title.rsplit(" - ", 1)[0].strip()
    return title


def item_date(item):
    raw = item.findtext("pubDate")
    if not raw:
        return None
    parsed = email.utils.parsedate_to_datetime(raw)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(WIB).date()


def main():
    by_title = {}
    request_count = 0
    for start, stop in windows():
        for query in QUERIES:
            if request_count:
                time.sleep(1.5)
            request_count += 1
            root = get_feed(query, start, stop)
            if root is None:
                continue
            for item in root.findall("./channel/item"):
                published = item_date(item)
                title = clean_title(item.findtext("title"))
                if not published or not (start <= published < stop):
                    continue
                lowered = title.casefold()
                if "ihsg" not in lowered and "indeks harga saham gabungan" not in lowered:
                    continue
                normalized = " ".join(lowered.split())
                if not title or normalized in by_title:
                    continue
                source_node = item.find("source")
                source = (source_node.text or "").strip() if source_node is not None else ""
                by_title[normalized] = {
                    "tanggal": published.isoformat(),
                    "judul": title,
                    "sumber": source,
                    "url": item.findtext("link", default="").strip(),
                    "query": query,
                }

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    rows = sorted(by_title.values(), key=lambda row: (row["tanggal"], row["judul"].casefold()))
    with OUTPUT.open("w", encoding="utf-8", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    days = {date.fromisoformat(row["tanggal"]) for row in rows}
    missing = [START + timedelta(days=i) for i in range((END - START).days)
               if START + timedelta(days=i) not in days]
    sources = {row["sumber"] for row in rows if row["sumber"]}
    print(f"Tersimpan {len(rows)} baris: {OUTPUT}")
    print(f"Rentang tanggal: {min(days) if days else '—'} hingga {max(days) if days else '—'}")
    print(f"Sumber unik: {len(sources)}")
    print("Tanggal tanpa data: " + (", ".join(day.isoformat() for day in missing) or "tidak ada"))


if __name__ == "__main__":
    main()
