# visdat

Materi mata kuliah **CAK4XBB3 Visualisasi Data**, S1 Informatika, Fakultas Informatika.

## Minggu-06: Visualisasi Data Time Series pada Saham (studi kasus ETF QQQ)

Deck `QQQ-Time-Series.pptx` (47 slide, Bahasa Indonesia) menjelaskan metode visualisasi time series
untuk data saham, mengikuti gaya `Minggu-06 Visualisasi Data Time Series.pptx`. Isinya:

1. Mengenal ETF dan QQQ (Invesco QQQ Trust, indeks Nasdaq-100, 10 holding terbesar, komposisi sektor).
2. Data time series saham (OHLCV, harga vs return, komponen time series).
3. Jenis plot: line, area, candlestick, seasonal plot, heatmap bulanan dan kalender, multiple time series, heatmap korelasi.
4. Tren dan smoothing: SMA, EMA, Bollinger Bands, fitting model, dekomposisi STL.
5. Metode tambahan: volatilitas bergulir, drawdown, RSI, MACD.

Materi bersifat edukasi dan bukan nasihat investasi.

## Struktur

| Jalur | Isi |
|---|---|
| `QQQ-Time-Series.pptx` | Deck hasil akhir |
| `SPEC.md` | Kontrak isi: rencana slide, daftar gambar, aturan data |
| `deck_numbers.md` | Judul slide bernomor, sumber dan cara hitung tiap angka |
| `data/` | Data hasil unduhan (QQQ, holdings, sektor, harga holding, `ASOF.txt`) |
| `figures/` | 22 gambar PNG 1600x900 yang dipakai di deck |
| `src/` | Kode: `fetch_data.py`, `charts/` (satu file per gambar), `build_deck.py` |
| `review/` | Laporan review independen (`SOL_REVIEW.md`, `SOL_REVIEW_2.md`) |

## Menjalankan ulang

Semua perintah memakai env Miniconda `py313`:

```bash
PY=~/miniconda3/envs/py313/bin/python
$PY src/fetch_data.py                 # unduh data (Yahoo Finance via yfinance)
$PY src/charts/run_a.py               # gambar bagian 1
$PY src/charts/run_b.py               # gambar bagian 2
$PY src/build_deck.py                 # bangun QQQ-Time-Series.pptx
```

`build_deck.py` membaca `Minggu-06 Visualisasi Data Time Series.pptx` sebagai template dari path
absolut pada konstanta `TEMPLATE` (`src/build_deck.py:13`, saat ini di akar checkout utama; file contoh
dosen itu tidak ikut di-commit, ubah path bila dijalankan di mesin lain). Build berhenti bila ada
placeholder kosong, judul isi lebih dari 32 karakter, atau gambar tanpa alt text.

## Catatan data

- Rentang: 18 Okt 2021 sampai 16 Okt 2026 (1.255 hari bursa); tanggal ambil ada di `data/ASOF.txt`.
- Komposisi dan bobot QQQ adalah potret saat data diunduh; angka berubah bila diunduh ulang.
- Bulan yang belum lengkap (Okt 2026) tidak dihitung sebagai observasi bulanan.
