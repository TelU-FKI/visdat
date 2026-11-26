# SPEC 2: Korpus artikel IHSG CNBC Indonesia (isi lengkap), Jan–9 Nov 2026

Mengganti SPEC_NEWS.md (yang hanya berisi judul). Format acuan dari dosen:
`/Users/rifkiwijaya/Downloads/Dataset Berita IHSG CNBC Indonesia untuk Analisis/cnbc_ihsg_articles.csv`
(556 artikel, 28 Jan–2 Apr 2026). Baca 3 baris pertama untuk melihat bentuknya. File itu hanya dibaca, jangan diubah.

## Keluaran per worker (kolom mentah, persis urutan ini, UTF-8)
`url,title,author,publish_date,keywords,content`
- `url`: URL artikel cnbcindonesia.com (kanonik, tanpa parameter).
- `title`: judul artikel apa adanya.
- `author`: penulis dari halaman artikel (jika tidak ada, "Redaksi").
- `publish_date`: `YYYY-MM-DD HH:MM:SS` waktu WIB.
- `keywords`: isi `<meta name="keywords">`, apa adanya.
- `content`: isi badan artikel, paragraf dipisah baris baru, tanpa iklan, tanpa "Baca juga", tanpa tag HTML, tanpa blok video/galeri. Mulai dari paragraf pertama ("Jakarta, CNBC Indonesia - ...") seperti di file acuan.

## Cara kerja
1. Temukan URL artikel di cnbcindonesia.com untuk jendela tanggal tugas: halaman tag (`/tag/ihsg`), halaman indeks per tanggal (`/indeks?date=YYYY-MM-DD`, ada paginasi), dan/atau sitemap. Periksa `robots.txt` dulu dan patuhi.
2. Simpan hanya artikel yang `keywords` atau `title`-nya memuat "ihsg" atau "indeks harga saham gabungan" (tak peka huruf besar) DAN tanggal terbitnya dalam jendela tugas.
3. Unduh tiap artikel sekali, urut, satu permintaan pada satu waktu (tanpa paralel di dalam worker), jeda >= 1,2 detik, User-Agent biasa, retry 2x. Jika menerima HTTP 403/429 atau halaman tantangan bot: BERHENTI, simpan yang sudah ada, dan laporkan. Jangan menembus login, paywall, atau proteksi bot.
4. Tulis ke CSV secara bertahap (agar bisa dilanjutkan) dan deduplikasi per `url`. Hanya teks yang benar-benar diambil dari halaman; jangan mengarang isi.
5. Skrip di `src/news/` (bisa dijalankan ulang dan melanjutkan), keluaran di `data/news/`. Python: `~/miniconda3/envs/py313/bin/python`; `requests`/`beautifulsoup4`/`lxml` boleh dipakai bila sudah terpasang, tanpa venv dan tanpa pemasangan paket baru. Jangan sentuh file lain. Jangan commit.
6. Lewati URL yang sudah ada di file acuan dosen (rentang 28 Jan–2 Apr 2026 sudah dipegang koordinator); tugas ada di luar rentang itu, kecuali tercantum lain.

## Pembagian
- A: 1–27 Jan 2026 dan 3 Apr–15 Jun 2026 -> `data/news/cnbc_A.csv`
- B: 16 Jun–31 Agu 2026 -> `data/news/cnbc_B.csv`
- C: 1 Sep–9 Nov 2026 -> `data/news/cnbc_C.csv`

Laporan akhir: jumlah artikel, rentang tanggal, jumlah artikel per bulan, panjang isi (median), jumlah artikel yang gagal diunduh, dan apakah ada pemblokiran.

## REVISI 1 (koordinator, sudah diverifikasi): sumber URL historis
Koreksi atas pembacaan robots.txt: larangan `/indeks` dan `*?` hanya berlaku untuk grup `User-agent: Googlebot`. Grup `User-agent: *` berisi `Allow: /`, jadi halaman tag berpaginasi BOLEH dipakai.
- `https://www.cnbcindonesia.com/indeks?date=...` mengabaikan tanggal (selalu terbaru) dan sitemap hanya 100 berita terbaru. JANGAN dipakai untuk riwayat.
- PAKAI `https://www.cnbcindonesia.com/tag/ihsg?page=N`: 10 artikel per halaman, urut terbaru ke lama. `page=1` membalas 301, gunakan `/tag/ihsg` dan ikuti redirect. Pemetaan terukur: page 5 ~ 4 Nov 2026, page 40 ~ 12 Okt, page 100 ~ 2 Agu, page 200 ~ 22 Apr 2026, page 400 ~ 23 Sep 2025. Cari batas jendela tugasmu dengan pencarian biner pada tanggal di URL (`/YYYYMMDDhhmmss-`), lalu baca semua halaman di rentang itu (beri margin 2 halaman).
- Tanggal terbit tiap artikel ada di awal segmen URL (`20260812xxxxxx`) dan di halaman artikel; pakai yang di halaman artikel untuk `publish_date`.
- Tetap berlaku: filter keywords/title memuat ihsg, jeda >= 1,2 detik, satu permintaan pada satu waktu, berhenti bila 403/429.
