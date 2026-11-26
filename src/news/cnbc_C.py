#!/usr/bin/env python3
"""Collect full CNBC Indonesia articles tagged IHSG for 1 Sep–9 Nov 2026."""

import csv
import re
import time
from datetime import date, datetime
from pathlib import Path
from urllib.parse import urljoin, urlsplit, urlunsplit

import requests
from bs4 import BeautifulSoup

START = date(2026, 9, 1)
END = date(2026, 11, 9)
BASE = "https://www.cnbcindonesia.com"
OUTPUT = Path(__file__).resolve().parents[2] / "data/news/cnbc_C.csv"
FIELDS = ("url", "title", "author", "publish_date", "keywords", "content")
HEADERS = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/131.0.0.0 Safari/537.36"}


def canonical(url):
    parts = urlsplit(url)
    return urlunsplit((parts.scheme, parts.netloc, parts.path.rstrip("/"), "", ""))


def get(session, url):
    for attempt in range(3):
        try:
            response = session.get(url, headers=HEADERS, timeout=30)
            if response.status_code in (403, 429):
                raise PermissionError(f"HTTP {response.status_code} at {url}")
            response.raise_for_status()
            text = response.text
            if "checking your browser" in text.lower() or "cf-chl-" in text:
                raise PermissionError(f"Bot challenge at {url}")
            return text
        except PermissionError:
            raise
        except requests.RequestException:
            if attempt == 2:
                raise
            time.sleep(2)


def tag_page_links(html):
    soup = BeautifulSoup(html, "html.parser")
    links = []
    for a in soup.select("article a[href]"):
        href = canonical(urljoin(BASE, a.get("href", "")))
        if ".cnbcindonesia.com/" not in href or not re.search(r"/\d{14}-\d+-\d+", href):
            continue
        title = " ".join(a.get_text(" ", strip=True).split())
        links.append((href, title))
    return links


def article_row(session, url):
    soup = BeautifulSoup(get(session, url), "html.parser")
    def meta(name):
        node = soup.find("meta", attrs={"name": name})
        return node.get("content", "").strip() if node else ""

    try:
        published = datetime.strptime(soup.select_one("meta[itemprop='datePublished']")["content"], "%Y/%m/%d %H:%M:%S")
    except (TypeError, KeyError, ValueError, AttributeError):
        raw = soup.select_one("meta[name='publishdate']")
        if not raw:
            raise ValueError("publish date missing")
        published = datetime.strptime(raw["content"], "%Y/%m/%d %H:%M:%S")
    if not START <= published.date() <= END:
        return None
    title_node = soup.find("meta", property="og:title")
    title = title_node.get("content", "").strip() if title_node else (soup.title.get_text(strip=True) if soup.title else "")
    keywords, author = meta("keywords"), meta("author") or "Redaksi"
    if not any(term in (keywords + " " + title).casefold() for term in ("ihsg", "indeks harga saham gabungan")):
        return None
    body = soup.select_one(".detail-text")
    if body is None:
        raise ValueError("article body missing")
    paragraphs = []
    for p in body.find_all("p"):
        text = " ".join(p.get_text(" ", strip=True).split())
        if not text or text.casefold().startswith("baca juga"):
            continue
        paragraphs.append(text)
    return dict(url=canonical(url), title=title, author=author,
                publish_date=published.strftime("%Y-%m-%d %H:%M:%S"),
                keywords=keywords, content="\n".join(paragraphs))


def main():
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    existing = {}
    if OUTPUT.exists():
        with OUTPUT.open(encoding="utf-8-sig", newline="") as f:
            existing = {r["url"]: r for r in csv.DictReader(f)}
    session = requests.Session()
    candidates = {}
    page = 1
    blocked = False
    last_request = 0.0
    while True:
        url = f"{BASE}/tag/ihsg" + (f"?page={page}" if page > 1 else "")
        wait = 1.2 - (time.monotonic() - last_request)
        if last_request and wait > 0:
            time.sleep(wait)
        try:
            html = get(session, url)
        except PermissionError as exc:
            print(f"BLOCKED: {exc}")
            blocked = True
            break
        except Exception as exc:
            print(f"FAILED listing page {page}: {exc}")
            break
        last_request = time.monotonic()
        links = tag_page_links(html)
        if not links:
            break
        oldest = None
        for link, title in links:
            match = re.search(r"/(\d{4})(\d{2})(\d{2})\d{6}-", link)
            if match:
                d = date(*(int(x) for x in match.groups()))
                oldest = d if oldest is None or d < oldest else oldest
                if START <= d <= END and ("ihsg" in title.casefold() or "indeks harga saham gabungan" in title.casefold()):
                    candidates.setdefault(link, title)
        if oldest is not None and oldest < START:
            break
        page += 1

    failed = 0
    previous = last_request
    for url in candidates:
        if url in existing:
            continue
        wait = 1.2 - (time.monotonic() - previous)
        if previous and wait > 0:
            time.sleep(wait)
        try:
            row = article_row(session, url)
            if row:
                existing[row["url"]] = row
        except PermissionError as exc:
            print(f"BLOCKED: {exc}")
            blocked = True
            break
        except Exception as exc:
            failed += 1
            print(f"FAILED {url}: {exc}")
        previous = time.monotonic()
        with OUTPUT.open("w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=FIELDS)
            writer.writeheader()
            writer.writerows(sorted(existing.values(), key=lambda r: (r["publish_date"], r["url"])))
    print(f"rows={len(existing)} candidates={len(candidates)} failed={failed} blocked={blocked} output={OUTPUT}")


if __name__ == "__main__":
    main()
