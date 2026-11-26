#!/usr/bin/env python3
"""Collect CNBC Indonesia articles tagged IHSG for shard A."""

import csv
import re
import statistics
import time
from datetime import date, datetime
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

import requests
from bs4 import BeautifulSoup


TAG_URL = "https://www.cnbcindonesia.com/tag/ihsg"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/131.0.0.0 Safari/537.36"
OUTPUT = Path(__file__).resolve().parents[2] / "data/news/cnbc_A.csv"
FIELDS = ("url", "title", "author", "publish_date", "keywords", "content")
WINDOWS = ((date(2026, 1, 1), date(2026, 1, 27)),
           (date(2026, 4, 3), date(2026, 6, 15)))
PAUSE = 1.3
DATE_IN_URL = re.compile(r"/(20\d{6})\d{6}-")
NEEDLES = ("ihsg", "indeks harga saham gabungan")


def canonical_url(url):
    parts = urlsplit(url.strip())
    return urlunsplit(("https", parts.netloc, parts.path, "", ""))


def url_day(url):
    match = DATE_IN_URL.search(url)
    return date(int(match[1][:4]), int(match[1][4:6]), int(match[1][6:8])) if match else None


def in_window(day):
    return day is not None and any(start <= day <= end for start, end in WINDOWS)


def matches(title, keywords):
    value = f"{title} {keywords}".casefold()
    return any(term in value for term in NEEDLES)


class Collector:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": USER_AGENT})
        self.last_request = 0.0
        self.blocked = False

    def get(self, url, retries=2):
        for attempt in range(retries + 1):
            delay = PAUSE - (time.monotonic() - self.last_request)
            if delay > 0:
                time.sleep(delay)
            try:
                response = self.session.get(url, timeout=35, allow_redirects=True)
                self.last_request = time.monotonic()
            except requests.RequestException as exc:
                self.last_request = time.monotonic()
                if attempt == retries:
                    print(f"Gagal unduh {url}: {exc}")
                    return None
                continue
            if response.status_code in (403, 429):
                self.blocked = True
                print(f"Berhenti karena HTTP {response.status_code}: {url}")
                return None
            if response.status_code >= 500 and attempt < retries:
                continue
            if response.status_code >= 400:
                print(f"Gagal unduh HTTP {response.status_code}: {url}")
                return None
            return response
        return None

    def tag_page(self, page):
        url = TAG_URL if page == 1 else f"{TAG_URL}?page={page}"
        response = self.get(url)
        if response is None:
            return []
        soup = BeautifulSoup(response.text, "html.parser")
        found = []
        seen = set()
        for anchor in soup.select('a[href*="/market/"]'):
            target = canonical_url(anchor.get("href", ""))
            if not DATE_IN_URL.search(target) or target in seen:
                continue
            seen.add(target)
            found.append((target, " ".join(anchor.stripped_strings)))
        return found

    def page_newest_day(self, page, cache):
        if page not in cache:
            cache[page] = self.tag_page(page)
        days = [url_day(url) for url, _ in cache[page]]
        days = [day for day in days if day]
        return max(days) if days else None

    def boundary_page(self, target, cache):
        """Find first page whose newest linked article is on/before target."""
        low, high = 1, 450
        answer = high
        while low <= high and not self.blocked:
            middle = (low + high) // 2
            newest = self.page_newest_day(middle, cache)
            if newest is None:
                # Empty/future pages indicate the high end of pagination.
                low = middle + 1
            elif newest <= target:
                answer = middle
                high = middle - 1
            else:
                low = middle + 1
        return answer


def parse_publish_date(soup):
    for attrs in ({"property": "article:published_time"}, {"name": "publishdate"},
                  {"name": "dtk:publishdate"}, {"name": "publish_date"}):
        tag = soup.find("meta", attrs=attrs)
        if tag and tag.get("content"):
            raw = tag["content"].strip()
            try:
                value = datetime.fromisoformat(raw.replace("Z", "+00:00"))
                if value.tzinfo:
                    # CNBC metadata uses WIB; normalize any offset to WIB.
                    from datetime import timedelta, timezone
                    value = value.astimezone(timezone(timedelta(hours=7)))
                return value.strftime("%Y-%m-%d %H:%M:%S")
            except ValueError:
                for fmt in ("%Y/%m/%d %H:%M:%S", "%Y-%m-%d %H:%M:%S"):
                    try:
                        return datetime.strptime(raw, fmt).strftime("%Y-%m-%d %H:%M:%S")
                    except ValueError:
                        pass
    return ""


def parse_article(url, response):
    soup = BeautifulSoup(response.text, "html.parser")
    title_tag = soup.find("meta", attrs={"property": "og:title"})
    title = (title_tag.get("content", "").strip() if title_tag else "")
    if not title:
        h1 = soup.select_one("h1")
        title = h1.get_text(" ", strip=True) if h1 else ""
    keyword_tag = soup.find("meta", attrs={"name": "keywords"})
    keywords = keyword_tag.get("content", "").strip() if keyword_tag else ""
    author_tag = soup.find("meta", attrs={"name": "author"})
    author = author_tag.get("content", "").strip() if author_tag else ""
    if not author:
        author = "Redaksi"

    body = soup.select_one(".detail-text, .detail__body-text")
    if body:
        for node in body.select("script, style, iframe, figure, .read__more, .detail__readmore, .box__video, .detail__video, .detail__gallery"):
            node.decompose()
        paragraphs = []
        for paragraph in body.find_all("p"):
            value = " ".join(paragraph.stripped_strings)
            if not value or re.search(r"^\s*baca\s*(?:juga|selengkapnya)\b", value, re.I):
                continue
            paragraphs.append(value)
        content = "\n".join(paragraphs)
    else:
        content = ""

    challenge = (soup.select_one("#challenge-form, .cf-challenge, .g-recaptcha") is not None or
                 bool(re.search(r"verify you are human|checking your browser|access denied", soup.title.get_text(" ", strip=True) if soup.title else "", re.I)))
    return {"url": url, "title": title, "author": author,
            "publish_date": parse_publish_date(soup), "keywords": keywords,
            "content": content}, challenge


def load_rows():
    rows = {}
    if OUTPUT.exists():
        with OUTPUT.open(encoding="utf-8-sig", newline="") as csvfile:
            for row in csv.DictReader(csvfile):
                if row.get("url"):
                    rows[row["url"]] = row
    return rows


def save_rows(rows):
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT.open("w", encoding="utf-8-sig", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(sorted(rows.values(), key=lambda r: r["publish_date"]))


def report(rows, failures, blocked):
    values = list(rows.values())
    days = [row["publish_date"][:10] for row in values if row["publish_date"]]
    by_month = {}
    lengths = []
    for row in values:
        month = row["publish_date"][:7]
        if month:
            by_month[month] = by_month.get(month, 0) + 1
        lengths.append(len(row["content"]))
    print(f"Jumlah artikel: {len(values)}")
    print(f"Rentang tanggal: {min(days) if days else '—'} sampai {max(days) if days else '—'}")
    print("Artikel per bulan: " + (", ".join(f"{k}: {v}" for k, v in sorted(by_month.items())) or "—"))
    print(f"Panjang isi median (karakter): {int(statistics.median(lengths)) if lengths else 0}")
    print(f"Gagal diunduh: {failures}")
    print(f"Pemblokiran: {'ya' if blocked else 'tidak'}")


def main():
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    rows = load_rows()
    collector = Collector()
    failures = 0
    cache = {}

    # Newest-to-oldest ordering on the tag; locate boundaries with binary search.
    starts = [collector.boundary_page(end, cache) for _, end in WINDOWS]
    ends = [collector.boundary_page(start, cache) for start, _ in WINDOWS]
    pages = set()
    for recent, older in zip(starts, ends):
        pages.update(range(max(1, recent - 2), min(450, older + 3)))

    links = {}
    for page in sorted(pages):
        if collector.blocked:
            break
        if page not in cache:
            cache[page] = collector.tag_page(page)
        for url, _title in cache[page]:
            day = url_day(url)
            # Include the two-page boundary margin. The URL timestamp is the
            # creation time; the page's published time is authoritative.
            if day:
                links[url] = day

    ordered = sorted(links, key=lambda url: (links[url], url))
    failures += sum(1 for page in cache.values() if page is None)
    checked = 0
    for url in ordered:
        if collector.blocked:
            break
        if url in rows:
            continue
        response = collector.get(url)
        if response is None:
            failures += 1
            save_rows(rows)
            if collector.blocked:
                break
            continue
        record, challenge = parse_article(url, response)
        if challenge:
            collector.blocked = True
            print(f"Berhenti: halaman tantangan bot terdeteksi pada {url}")
            break
        if not record["title"] or not record["publish_date"] or not record["content"]:
            failures += 1
        else:
            try:
                published = datetime.strptime(record["publish_date"], "%Y-%m-%d %H:%M:%S").date()
            except ValueError:
                published = None
            if in_window(published) and matches(record["title"], record["keywords"]):
                rows[url] = record
        checked += 1
        save_rows(rows)
        if checked % 50 == 0:
            print(f"Diperiksa {checked}/{len(ordered)} URL; tersimpan {len(rows)} artikel")

    save_rows(rows)
    report(rows, failures, collector.blocked)


if __name__ == "__main__":
    main()
