# SPEC: Korpus berita IHSG (Minggu-09, word cloud)

Tujuan: satu CSV berisi >1000 judul berita IHSG, Jan 2026 sampai 9 Nov 2026, Bahasa Indonesia.

Sumber: Google News RSS (terverifikasi bisa diakses tanpa login):
`https://news.google.com/rss/search?q=<query>+after:YYYY-MM-DD+before:YYYY-MM-DD&hl=id&gl=ID&ceid=ID:id`
Maks ~100 item per permintaan, jadi pecah per jendela 7 hari (after inklusif, before eksklusif).
Query minimal: `IHSG`, `IHSG ditutup`, `indeks harga saham gabungan`, `IHSG hari ini saham`.
Gunakan `urllib` + `xml.etree`, header User-Agent Mozilla, jeda >=1,5 detik antar permintaan, coba ulang 2x. Jangan scraping isi artikel, jangan lewati login/paywall.

Kolom CSV (UTF-8, header persis ini):
`tanggal` (YYYY-MM-DD dari pubDate, zona WIB), `judul` (tanpa akhiran " - Sumber"), `sumber`, `url` (link RSS apa adanya), `query`.

Aturan:
- Hanya simpan item yang tanggalnya masuk jendela tugas dan judul memuat IHSG atau "indeks harga saham gabungan" (tidak peka huruf besar).
- Deduplikasi per shard berdasarkan judul ternormalisasi (huruf kecil, spasi rapi).
- Jangan mengarang atau menulis judul sendiri; semua baris harus berasal dari RSS.
- Skrip di `src/news/` (satu skrip per worker, bisa dijalankan ulang), keluaran di `data/news/`.
- Python: `~/miniconda3/envs/py313/bin/python`. Tanpa venv, tanpa paket baru.
- Jangan sentuh file di luar `src/news/` dan `data/news/`. Jangan commit.
- Laporkan: jumlah baris, rentang tanggal, jumlah sumber unik, tanggal tanpa data.

Pembagian: A = 1 Jan–31 Mar 2026 -> `data/news/shard_A.csv`; B = 1 Apr–30 Jun 2026 -> `shard_B.csv`; C = 1 Jul–9 Nov 2026 (before 2026-11-10) -> `shard_C.csv`. Target tiap shard >=350 baris.
