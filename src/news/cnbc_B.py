#!/usr/bin/env python3
"""Collect full CNBC Indonesia IHSG articles for shard B (16 Jun–31 Aug 2026)."""

import csv
import re
import time
from datetime import date, datetime
from pathlib import Path
from urllib.parse import urlparse, urlunparse

import requests
from bs4 import BeautifulSoup


START = date(2026, 6, 16)
END = date(2026, 8, 31)
BASE = "https://www.cnbcindonesia.com"
OUTPUT = Path(__file__).resolve().parents[2] / "data/news/cnbc_B.csv"
FIELDS = ("url", "title", "author", "publish_date", "keywords", "content")
HEADERS = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/130.0.0.0 Safari/537.36"}
MONTHS = {"January": 1, "February": 2, "March": 3, "April": 4, "May": 5,
          "June": 6, "July": 7, "August": 8, "September": 9, "October": 10,
          "November": 11, "December": 12,
          "Januari": 1, "Februari": 2, "Maret": 3, "April": 4, "Mei": 5,
          "Juni": 6, "Juli": 7, "Agustus": 8, "September": 9, "Oktober": 10,
          "November": 11, "Desember": 12}


class Blocked(Exception):
    pass


def get(session, url, last_request):
    if last_request[0] is not None:
        time.sleep(max(0, 1.2 - (time.monotonic() - last_request[0])))
    for attempt in range(3):
        try:
            response = session.get(url, headers=HEADERS, timeout=30)
            last_request[0] = time.monotonic()
            if response.status_code in (403, 429):
                raise Blocked(f"HTTP {response.status_code} pada {url}")
            response.raise_for_status()
            if "captcha" in response.text[:5000].lower() or "verify you are human" in response.text[:5000].lower():
                raise Blocked(f"Tantangan bot pada {url}")
            return response.text
        except Blocked:
            raise
        except requests.RequestException:
            if attempt == 2:
                return None
            time.sleep(1.2)
    return None


def article_date_from_url(url):
    match = re.search(r"/(\d{8})\d{6}-", urlparse(url).path)
    if not match:
        return None
    return datetime.strptime(match.group(1), "%Y%m%d").date()


def read_existing():
    rows = {}
    if OUTPUT.exists():
        with OUTPUT.open(encoding="utf-8", newline="") as f:
            for row in csv.DictReader(f):
                if row.get("url"):
                    rows[row["url"]] = row
    return rows


def parse_article(html, url):
    soup = BeautifulSoup(html, "lxml")
    canonical = soup.find("link", rel="canonical")
    if canonical and canonical.get("href"):
        url = urlunparse(urlparse(canonical["href"])._replace(query="", fragment=""))
    title_node = soup.select_one("h1.detail-title") or soup.find("h1")
    title = title_node.get_text(" ", strip=True) if title_node else ""
    keyword_node = soup.select_one('meta[name="keywords"]')
    keywords = keyword_node.get("content", "").strip() if keyword_node else ""
    lowered = (title + " " + keywords).casefold()
    if "ihsg" not in lowered and "indeks harga saham gabungan" not in lowered:
        return None
    author_node = soup.select_one('meta[name="author"]')
    author = author_node.get("content", "").strip() if author_node else ""
    if not author:
        head = soup.select_one(".detail-head")
        text = head.get_text(" ", strip=True) if head else ""
        author = text.split("CNBC Indonesia", 1)[0].strip(" ,") if "CNBC Indonesia" in text else "Redaksi"
    date_text = ""
    head = soup.select_one(".detail-head")
    if head:
        text = head.get_text(" ", strip=True)
        month_names = "|".join(MONTHS)
        match = re.search(rf"(\d{{1,2}})\s+({month_names})\s+(\d{{4}})\s+(\d{{2}}:\d{{2}})", text)
        if match:
            day, month, year, hm = match.groups()
            date_text = datetime(int(year), MONTHS[month], int(day), int(hm[:2]), int(hm[3:]), 0).strftime("%Y-%m-%d %H:%M:%S")
    if not date_text:
        time_node = soup.select_one('meta[property="article:published_time"]')
        if time_node and time_node.get("content"):
            try:
                date_text = datetime.fromisoformat(time_node["content"].replace("Z", "+00:00")).astimezone().strftime("%Y-%m-%d %H:%M:%S")
            except ValueError:
                pass
    if not date_text:
        return None
    published_day = datetime.strptime(date_text, "%Y-%m-%d %H:%M:%S").date()
    if not (START <= published_day <= END):
        return None
    body = next((node for node in soup.select(".detail-text")
                 if node.find("p", recursive=False)), None)
    paragraphs = []
    if body:
        for p in body.find_all("p"):
            if p.find_parent(class_="detail-text") is not body:
                continue
            text = p.get_text(" ", strip=True)
            low = text.casefold()
            if not text or "baca juga" in low or "saksikan video" in low or "lihat juga" in low:
                continue
            paragraphs.append(text)
    return {"url": url, "title": title, "author": author or "Redaksi", "publish_date": date_text,
            "keywords": keywords, "content": "\n".join(paragraphs)}


def write_rows(rows):
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(sorted(rows.values(), key=lambda r: (r["publish_date"], r["url"])))


def main():
    rows = read_existing()
    failures, blocked = 0, False
    session, last_request = requests.Session(), [None]
    # Repair interrupted/older output rows whose metadata was saved before body
    # extraction completed; each article request remains strictly sequential.
    for url, old_row in list(rows.items()):
        if old_row.get("content"):
            continue
        try:
            html = get(session, url, last_request)
        except Blocked as exc:
            blocked = True
            print(f"PEMBLOKIRAN: {exc}", flush=True)
            break
        if html is None:
            failures += 1
            continue
        try:
            repaired = parse_article(html, url)
        except Exception:
            repaired = None
        if repaired:
            rows[repaired["url"]] = repaired
            write_rows(rows)
    seen = set()
    # Around page 70 the rolling tag archive reaches late August 2026; starting
    # nearby avoids needlessly refetching many years of unrelated archive pages.
    page = 70
    try:
        while not blocked and page < 1001:
            list_url = f"{BASE}/tag/ihsg" + (f"?page={page}" if page > 1 else "")
            html = get(session, list_url, last_request)
            if html is None:
                failures += 1
                page += 1
                continue
            soup = BeautifulSoup(html, "lxml")
            urls = []
            for link in soup.select('a[href*="cnbcindonesia.com/market/"]'):
                url = urlunparse(urlparse(link.get("href", ""))._replace(query="", fragment=""))
                day = article_date_from_url(url)
                if day and url not in seen:
                    seen.add(url)
                    urls.append((day, url))
            dated = [day for day, _ in urls]
            if dated and max(dated) < START:
                break
            for day, url in urls:
                if day < START:
                    continue
                if day > END or (url in rows and rows[url].get("content")):
                    continue
                article_html = get(session, url, last_request)
                if article_html is None:
                    failures += 1
                    continue
                try:
                    row = parse_article(article_html, url)
                except Exception:
                    failures += 1
                    continue
                if row:
                    rows[row["url"]] = row
                    write_rows(rows)
                    print(f"Simpan {row['publish_date']} {row['title']}", flush=True)
            print(f"Halaman tag {page}: {len(urls)} URL, total {len(rows)}", flush=True)
            if not urls:
                break
            page += 1
    except Blocked as exc:
        blocked = True
        print(f"PEMBLOKIRAN: {exc}", flush=True)
    write_rows(rows)
    print_report(rows, failures, blocked)


def print_report(rows, failures, blocked):
    dates = sorted(datetime.strptime(row["publish_date"], "%Y-%m-%d %H:%M:%S").date() for row in rows.values())
    lengths = sorted(len(row["content"]) for row in rows.values())
    median = (lengths[(len(lengths)-1)//2] + lengths[len(lengths)//2]) / 2 if lengths else 0
    print("\nLAPORAN SHARD B")
    print(f"Jumlah artikel: {len(rows)}")
    print(f"Rentang tanggal: {dates[0] if dates else '—'} – {dates[-1] if dates else '—'}")
    counts = {}
    for row in rows.values():
        month = row["publish_date"][:7]
        counts[month] = counts.get(month, 0) + 1
    for month in ("2026-06", "2026-07", "2026-08"):
        print(f"Artikel per bulan {month}: {counts.get(month, 0)}")
    print(f"Panjang isi median: {median:.0f} karakter")
    print(f"Artikel gagal diunduh: {failures}")
    print(f"Pemblokiran: {'ya' if blocked else 'tidak'}")


if __name__ == "__main__":
    main()
