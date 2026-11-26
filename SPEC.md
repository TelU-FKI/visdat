# SPEC — Visualisasi Time Series Saham dengan ETF QQQ

Deliverable: `QQQ-Time-Series.pptx` (16:9, **seluruhnya Bahasa Indonesia**), gaya mengikuti
`/Users/rifkiwijaya/Developer/visdat/Minggu-06 Visualisasi Data Time Series.pptx`
(mata kuliah CAK4XBB3 Visualisasi Data, S1 Informatika, Fakultas Informatika).
Pola contoh: setiap metode = 1 slide teks (definisi, cara baca) + 1 slide gambar.

## Aturan umum
- Python hanya lewat `~/miniconda3/envs/py313/bin/python` (jangan buat venv, jangan install paket baru;
  yfinance, pptx, matplotlib, pandas, statsmodels, mplfinance, scipy sudah ada).
- Data: `yfinance`, ticker `QQQ`, 5 tahun terakhir, `auto_adjust=False`. Simpan ke `data/qqq_ohlcv.csv`.
  Holdings dan sektor dari `yf.Ticker('QQQ').funds_data` → `data/holdings_top.csv`, `data/sector_weights.csv`.
  Tulis tanggal pengambilan data di `data/ASOF.txt`; angka di slide harus sama persis dengan data.
- Jangan mengarang fakta. Fakta di luar SPEC ini dan data hasil unduhan: jangan dimasukkan.
- Bukan nasihat investasi — wajib ada slide disclaimer.
- Gambar: PNG 1600x900 px (dpi 200, figsize 8x4.5), label sumbu, judul, legenda, dan angka **berbahasa Indonesia**
  (format tanggal "Jan 2024"). Palet konsisten satu tema; warna tidak boleh jadi satu-satunya
  pembeda (pakai gaya garis/label juga). Tidak ada teks terpotong atau saling tumpang tindih.
- Satu slide = satu ide. Maks 6 butir/slide, kalimat pendek. Rumus ditulis sebagai teks yang terbaca.
- Struktur kode: banyak file kecil, fungsi < 50 baris, tanpa nilai ajaib (konstanta bernama).

## Catatan data (sudah diambil oleh Claude: `python src/fetch_data.py`, jangan diunduh ulang)
- `data/qqq_ohlcv.csv` (indeks `Date`; kolom Open, High, Low, Close, Adj Close, Volume; 1255 baris, s.d. 2026-10-16)
- `data/holdings_top.csv` (Symbol, Name, Holding Percent sebagai pecahan), `data/sector_weights.csv` (Sektor, Bobot pecahan),
  `data/constituents_close.csv` (Close 10 holding terbesar), `data/ASOF.txt`.
- Kunci sektor berbahasa Inggris → **terjemahkan ke Indonesia** di gambar dan slide: technology=Teknologi, communication_services=Layanan Komunikasi,
  consumer_cyclical=Konsumsi Siklikal, consumer_defensive=Konsumsi Defensif, industrials=Industri, healthcare=Kesehatan, utilities=Utilitas,
  basic_materials=Bahan Baku, energy=Energi, financial_services=Jasa Keuangan, realestate=Properti.
- GOOGL dan GOOG adalah dua kelas saham Alphabet (satu perusahaan) → catat di slide holdings dan di heatmap korelasi (korelasi ≈ 1 wajar).
- Panggil `from common import ...` (`src/charts/common.py`): palet, `apply_style()`, loader, `format_date_axis()`, `save_fig()`. Jangan ubah file itu;
  kalau perlu perubahan, tulis di laporan akhir.

## Daftar gambar (nama file tetap, di `figures/`)
| File | Isi |
|---|---|
| 00_harga_vs_return.png | 2 panel: harga penutupan vs return harian (harga tidak stasioner, return berayun di sekitar 0) |
| 01_line_close.png | Line plot harga penutupan 5 tahun |
| 02_area_volume.png | Area plot volume perdagangan (juta lembar), dengan rata-rata bergulir |
| 03_candlestick.png | Candlestick + volume, ±120 hari bursa terakhir (mplfinance, warna naik/turun + simbol) |
| 04_seasonal_plot.png | Seasonal plot: return kumulatif per bulan, satu garis per tahun |
| 05_heatmap_bulanan.png | Heatmap return bulanan (baris tahun, kolom bulan), skala diverging berpusat di 0 |
| 06_heatmap_kalender.png | Calendar heatmap return harian 12 bulan terakhir (minggu × hari) |
| 07_multi_overlay.png | QQQ + 5 holding terbesar, dinormalisasi indeks=100 pada awal periode (satu panel) |
| 08_multi_small.png | Data yang sama, small multiples (panel terpisah, sumbu y sama) |
| 09_korelasi.png | Heatmap korelasi return harian: QQQ + 10 holding terbesar (angka di sel) |
| 10_sma.png | Harga + SMA 20, 50, 200 |
| 11_ema_vs_sma.png | EMA 50 vs SMA 50 pada 1 tahun terakhir (tampilkan jeda/lag) |
| 12_bollinger.png | Bollinger Bands (20, 2σ) 1 tahun terakhir + %B kecil di bawah |
| 13_fitting.png | Fitting tren: linear, polinomial derajat 3, dan eksponensial (log-linear); sertakan R² di legenda |
| 14_dekomposisi.png | STL pada log harga: observasi, tren, musiman, residual (4 panel) |
| 15_return_volatilitas.png | Return harian + volatilitas bergulir 21 hari (anualisasi) |
| 16_drawdown.png | Underwater plot drawdown dari puncak; tandai drawdown maksimum |
| 17_rsi.png | Harga + RSI(14) dengan garis 30/70, 1 tahun terakhir |
| 18_macd.png | Harga + MACD(12,26,9) dengan histogram, 1 tahun terakhir |
| 19_sektor.png | Bar horizontal bobot sektor QQQ (dari data) |
| 20_top_holdings.png | Bar horizontal 10 holding terbesar dengan bobot % (dari data) |

## Rencana slide (±52 slide)
Poin kunci per slide; Codex mengembangkan jadi kalimat Indonesia ringkas. Gambar = slide gambar terpisah setelah slide teks.

**Pembuka**
1. Judul: "Visualisasi Data Time Series pada Saham: Studi Kasus ETF QQQ" + identitas kuliah seperti contoh.
2. Agenda (5 bagian).

**Bagian 1 — Mengenal ETF dan QQQ**
3. Apa itu ETF (Exchange-Traded Fund): keranjang aset yang diperdagangkan di bursa seperti saham; umumnya melacak indeks; harga bergerak sepanjang hari bursa.
4. Ciri ETF: diversifikasi dalam satu instrumen, biaya relatif rendah (expense ratio), transparan (komposisi dipublikasikan), likuid. Bandingkan singkat dengan membeli satu saham dan reksa dana (tabel 3 kolom).
5. Apa itu QQQ: Invesco QQQ Trust, ETF yang melacak indeks Nasdaq-100; ticker QQQ; mulai diperdagangkan Maret 1999; expense ratio dari data yfinance.
6. Nasdaq-100: 100 perusahaan non-keuangan terbesar yang tercatat di Nasdaq; bobot berbasis kapitalisasi pasar (dimodifikasi); rebalancing berkala. Indeks mengecualikan perusahaan sektor keuangan menurut klasifikasi indeks sendiri; klasifikasi sektor Yahoo bisa berbeda (data menunjukkan "financial services" 0,19%), jadi tulis dengan hati-hati dan jangan klaim "nol".
7. QQQ terdiri dari saham apa saja: tabel top holdings (data).
8. Gambar 20_top_holdings.png + catatan: konsentrasi pada beberapa saham teknologi besar (hitung total bobot 10 teratas dari data).
9. Gambar 19_sektor.png + penjelasan dominasi sektor (dari data).
10. Mengapa QQQ cocok jadi contoh time series: likuid, data harian panjang, ada tren, volatilitas, periode krisis/pemulihan.

**Bagian 2 — Data time series saham**
11. Data OHLCV: Open, High, Low, Close, Adj Close, Volume (tabel contoh 5 baris asli dari data). Frekuensi harian, hari bursa saja (tidak ada akhir pekan/libur → indeks waktu tidak kontinu).
12. Harga vs return: return = (P_t − P_{t−1}) / P_{t−1}; harga tidak stasioner, return mendekati stasioner. Lalu gambar 00.
13. Komponen time series versi saham: tren, musiman (lemah), siklus (siklus ekonomi/suku bunga), noise/acak. Peringatan: pola musiman pada saham lemah dan tidak menjamin berulang.
14. Jenis plot yang dipakai (ringkasan: line, area, candlestick, seasonal, heatmap, multiple series, heatmap korelasi).

**Bagian 3 — Jenis plot**
- Line plot (teks + 01). Cocok: tren dan laju perubahan; hindari skala y terpotong yang menyesatkan; skala log untuk periode panjang.
- Area plot (teks + 02). Cocok untuk volume/kuantitas; tidak dipakai untuk membandingkan banyak seri.
- Candlestick (teks + 03). Anatomi: badan = open–close, sumbu = high–low; naik vs turun. Satu candle memuat 4 harga.
- Seasonal plot (teks + 04). Membelah tahun-tahun untuk membandingkan pola per bulan; baca dengan hati-hati.
- Heatmap bulanan (teks + 05) — pola bulan×tahun.
- Heatmap kalender (gambar 06 dengan judul + 2 butir catatan).
- Multiple time series: teks (normalisasi indeks=100, mengapa tidak plot harga mentah), gambar 07 overlay, gambar 08 small multiples; bandingkan kelebihan keduanya.
- Heatmap korelasi (teks + 09). Korelasi return, bukan harga; korelasi tinggi = diversifikasi terbatas.

**Bagian 4 — Visualisasi tren dan smoothing**
- Mengapa tren lebih penting dari detail: noise harian; smoothing = kurangi fluktuasi kecil, tonjolkan pola utama; harga yang dihaluskan punya jeda (lag).
- Simple Moving Average (rumus SMA_t = (1/n)·Σ P_{t−i}; teks + 10). Window 20/50/200 hari; "golden cross"/"death cross" hanya istilah populer, bukan sinyal pasti.
- Exponential Moving Average (EMA_t = α·P_t + (1−α)·EMA_{t−1}, α = 2/(n+1); teks + 11). Bobot lebih besar ke data baru.
- Bollinger Bands (MA20 ± 2σ; %B; teks + 12). Mengukur volatilitas relatif; pita menyempit/melebar.
- Fitting model matematika (linear, polinomial, eksponensial; teks + 13). Risiko overfitting & ekstrapolasi; R² tinggi pada tren ≠ kemampuan prediksi.
- Dekomposisi time series (STL: observasi = tren + musiman + residual; teks + 14).

**Bagian 5 — Metode tambahan khas pasar saham**
- Return & volatilitas bergulir (std × √252; teks + 15). Volatility clustering.
- Drawdown (teks + 16).
- RSI (rumus ringkas; teks + 17). Indikator momentum 0–100; 30/70 sebagai konvensi.
- MACD (EMA12 − EMA26, sinyal EMA9; teks + 18).

**Penutup**
- Ringkasan: tabel metode → pertanyaan yang dijawab → kapan dipakai → kelemahan.
- Disclaimer: materi edukasi, bukan nasihat investasi; kinerja masa lalu tidak menjamin masa depan.
- Referensi: Wilke (2019) Fundamentals of Data Visualization; Hyndman & Athanasopoulos, Forecasting: Principles and Practice (3rd ed.); Bollinger (2001) Bollinger on Bollinger Bands; Wilder (1978) New Concepts in Technical Trading Systems; Appel (MACD); halaman resmi Invesco QQQ & Nasdaq-100; Yahoo Finance via yfinance (sebutkan tanggal akses dari data/ASOF.txt).

## Struktur repo (worktree ini)
```
SPEC.md  data/  figures/  src/  QQQ-Time-Series.pptx
src/fetch_data.py   src/charts/*.py   src/build_deck.py
```
