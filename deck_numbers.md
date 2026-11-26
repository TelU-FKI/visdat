# Catatan angka deck QQQ

Sumber harga/holding/sektor: berkas lokal `data/`; Yahoo Finance via yfinance. Tanggal pengambilan: 2026-10-19.

## Angka hasil data

- Rentang harga: 2021-10-18 sampai 2026-10-16; jumlah baris: 1,255. Tanggal rentang berasal dari nilai minimum/maksimum indeks dan jumlah dari banyaknya baris CSV.
- Penutupan terakhir: 709,80 USD; diambil dari nilai terakhir kolom `Close`.
- Total bobot sepuluh holding teratas: 46,69%; jumlah `Holding Percent` pada 10 baris pertama × 100.
- Holding berasal dari `data/holdings_top.csv`; persen per baris = nilai pecahan × 100.
- Sektor pada CSV (persen = pecahan × 100): realestate: 0,00%, consumer_cyclical: 10,07%, basic_materials: 0,92%, consumer_defensive: 5,56%, technology: 60,33%, communication_services: 12,59%, financial_services: 0,19%, utilities: 1,01%, industrials: 5,11%, energy: 0,45%, healthcare: 3,79%.

| Simbol | Nama | Bobot (%) |
|---|---|---:|
| NVDA | NVIDIA Corp | 8,33 |
| AAPL | Apple Inc | 7,35 |
| MSFT | Microsoft Corp | 5,76 |
| MU | Micron Technology Inc | 5,02 |
| AMD | Advanced Micro Devices Inc | 4,17 |
| AMZN | Amazon.com Inc | 4,07 |
| META | Meta Platforms Inc Class A | 3,26 |
| GOOGL | Alphabet Inc Class A | 3,05 |
| GOOG | Alphabet Inc Class C | 2,85 |
| TSLA | Tesla Inc | 2,82 |

- Sampel OHLCV di slide: lima baris terakhir `data/qqq_ohlcv.csv`; tabel menampilkan tanggal dan angka asli.

| Tanggal | Open | High | Low | Close | Adj Close | Volume |
|---|---:|---:|---:|---:|---:|---:|
| 2026-10-12 | 749,69 | 749,79 | 744,85 | 746,04 | 746,04 | 25.147.700 |
| 2026-10-13 | 739,52 | 744,20 | 738,83 | 743,57 | 743,57 | 28.738.600 |
| 2026-10-14 | 737,98 | 740,53 | 726,39 | 728,95 | 728,95 | 52.383.600 |
| 2026-10-15 | 718,55 | 729,43 | 715,44 | 728,00 | 728,00 | 49.828.700 |
| 2026-10-16 | 725,52 | 725,96 | 707,23 | 709,80 | 709,80 | 66.693.300 |

## Angka terverifikasi lain dan cara baca

Nilai berikut telah disediakan dan diverifikasi dalam tugas: expense ratio 0,18%; total sepuluh bobot teratas 46,69%; return bulanan terbaik Apr 2026 +15,69% dan terburuk Apr 2022 −13,60%; korelasi GOOGL–GOOG 0,997, AAPL–MU 0,310, QQQ–NVDA 0,78; R² linear 0,8489, polinomial derajat 3 0,9481, eksponensial 0,8954; drawdown maksimum −35,62% pada 28 Des 2022; volatilitas 21 hari 18,04% tahunan; RSI Wilder(14) 35,00; MACD(12,26,9) 1,525, sinyal 6,167, histogram −4,642.

- Korelasi dihitung antar-return harian; R² memakai residual kuadrat terhadap jumlah kuadrat total pada sampel harga yang sama.
- Drawdown = harga / puncak berjalan − 1. Volatilitas = simpangan baku sampel return 21 hari × √252.
- RSI menggunakan inisialisasi rata-rata sederhana 14 perubahan lalu pembaruan Wilder; MACD adalah EMA12 − EMA26 dengan garis sinyal EMA9.
- STL memakai 60 `Close` akhir bulan lengkap, Okt 2021–Sep 2026, log harga, period=12, seasonal=99, seasonal_deg=0, non-robust. Rentang aktual tren 5,682251–6,596293 log; musiman −0,036262–0,028384; residual −0,128356–0,084856; simpangan baku residual 0,046309.
- Profil musiman aktual per bulan (komponen × 100): Jan 0,6%, Feb −1,3%, Mar −2,0%, Apr −3,6%, Mei 1,4%, Jun 2,0%, Jul 2,8%, Agu 1,5%, Sep −1,1%, Okt −2,0%, Nov 1,7%, Des 0,1%. Lima siklus lengkap ini merupakan pengamatan, bukan klaim pengulangan.
- Dari 60 harga penutupan bulanan lengkap diperoleh 59 return bulanan; Oktober 2026 parsial tidak masuk pengamatan.
- Koefisien EMA 50: α=2/(50+1)=0,03921569 (≈0,039). %B terakhir = (Close−pita bawah)/(pita atas−pita bawah) = −0,221624; pita memakai SMA20 ±2 simpangan baku sampel (ddof=1).
- Pada 16 Okt 2026: SMA20 742,52 USD, SMA50 726,77 USD, EMA50 727,94 USD; semuanya dihitung dari `Close` lokal dengan jendela 20/50 hari dan EMA `adjust=False`.

## Daftar judul slide

01. Visualisasi Data Time Series pada Saham: Studi Kasus ETF QQQ
02. Agenda
03. Istilah penting
04. Apa itu ETF?
05. Cara kerja ETF
06. Ciri ETF dalam satu pandangan
07. Mengenal QQQ
08. Profil holding terbesar
09. Indeks Nasdaq-100
10. Sepuluh holding terbesar: tabel
11. Sepuluh holding terbesar: bobot
12. Komposisi sektor QQQ
13. QQQ sebagai deret waktu
14. Contoh data OHLCV QQQ
15. Harga dan return
16. Komponen time series saham
17. Jenis plot yang digunakan
18. Bagian I: Grafik harga
19. Plot garis
20. Plot area volume
21. Candlestick
22. Plot musiman
23. Heatmap return bulanan
24. Heatmap kalender return harian
25. Membandingkan beberapa seri
26. Bagian II: Membandingkan aset
27. QQQ dan lima holding: overlay
28. Small multiples QQQ
29. Heatmap korelasi return
30. Korelasi return harian
31. Mengapa tren perlu dihaluskan?
32. Rata-rata sederhana (SMA)
33. Rata-rata eksponensial (EMA)
34. Bollinger Bands
35. Fitting tren matematis
36. Dekomposisi STL
37. Dekomposisi STL bulanan
38. Profil musiman bulanan
39. Return dan volatilitas
40. Drawdown
41. RSI (14)
42. MACD (12, 26, 9)
43. Ringkasan metode (1/2)
44. Ringkasan metode (2/2)
45. Disclaimer
46. Referensi buku dan artikel
47. Sumber resmi dan data

## QA render dan batas verifikasi

Deck 47 slide dibangun ulang, dirender ke PDF oleh LibreOffice, lalu menjadi 47 PNG dengan `pdftoppm`. Inspeksi visual meliputi slide 22–24, 34–38, 39–44, dan sampel acak 19, 20, 26, 32, 45; tidak terlihat teks meluap atau bertabrakan dengan gambar/footer. Sebelum perbaikan ditemukan 58 placeholder teks kosong; validasi builder menghapus semuanya (0 tersisa). Pemeriksaan mekanis memastikan judul isi ≤32 karakter, tidak ada bullet literal, bentuk di luar kanvas, atau teks eksplisit di bawah 14 pt di luar tabel; 22 gambar memiliki alt text dan 3 hyperlink aktif. Slide 24 menggunakan tiga paragraf bullet asli berukuran 14 pt.

Fakta eksternal selain yang tercantum dalam SPEC/data lokal tidak diverifikasi secara independen; deck hanya memakai materi yang ditentukan tugas dan nilai dari berkas lokal.

## Perubahan putaran perbaikan

### Putaran perbaikan 6

1. Slide fitting dan catatan menyatakan R² ketiga model memakai rumus/skala/sampel yang sama dan dapat dibandingkan untuk kecocokan dalam sampel; eksponensial dipasang pada log harga, polinomial lebih fleksibel, dan kecocokan bukan prediksi. Tabel slide 44 memakai keterbatasan “Cocok dalam sampel bukan prediksi”.
2. Slide 24 serta catatannya menyebut rentang Nov 2025–Okt 2026; Oktober hanya sampai 16 Okt.
3. Slide 36, 37, dan 38 menjelaskan komponen musiman bersatuan log serta batang profil berupa log ×100 (≈%), bukan persen eksak 100×(exp(s)−1).
4. Grafik teks+gambar diperbesar ke lebar 6,97 inci pada x=6,26; kolom teks dipersempit ke 5,80 inci. Teks kalender slide 24 diringkas untuk menyatakan cakupan yang tepat dan slide 35 dirumuskan ulang; slide 22–23 serta 34–42 muat tanpa pemangkasan tambahan.

### Putaran perbaikan 5

1. Placeholder kosong (58 sebelum) dihapus pada semua slide; builder gagal jika placeholder kosong masih ada.
2. Slide kalender memakai tiga butir asli berukuran 14 pt dan gambar sedikit lebih kecil; tidak ada bullet yang diketik sebagai karakter isi.
3. Builder memeriksa judul, bullet literal, posisi bentuk, ukuran teks, alt text, dan hyperlink sebelum menyimpan.

### Putaran perbaikan 4

1. Judul isi dipendekkan menjadi ≤32 karakter dan pemeriksaan batas judul ditambahkan ke builder; judul QQQ kini satu baris.
2. Plot musiman dan catatan menyebut empat tahun penuh (2022–2025), dua parsial, dan garis putus-putus untuk tahun parsial.
3. Small multiples dan catatannya menjelaskan sumbu x/y linear bersama serta dampak skala MU/NVDA; overlay tetap dijelaskan sebagai skala log.
4. Semua negatif numerik memakai tanda minus Unicode; tanda hubung istilah serta Nasdaq-100 dan tanggal tetap sebagai tanda hubung.
5. Gambar penuh diperbesar selebar area aman; slide kalender dengan butir memakai lebar 8,60 inci agar ruang penjelasan dan footer tetap terjaga.
6. Rujukan dipecah menjadi buku/artikel dan sumber resmi/data; tiga hyperlink tetap aktif.

1. Plot musiman menyatakan enam tahun kalender, dua parsial, garis putus-putus untuk tahun parsial.
2. Heatmap bulanan mengeluarkan Oktober 2026 parsial; slide heatmap menyebut batas 16 Okt dan 2021 hanya Nov–Des.
3. STL/profil/ringkasan memakai 60 akhir bulan Okt 2021–Sep 2026 dan nilai baru; profil lima siklus adalah pengamatan.
4. Fitting menjelaskan bahwa R² harga pada sampel sama dapat dibandingkan untuk kecocokan dalam sampel, meski eksponensial dipasang pada log harga; kecocokan bukan prediksi.
5. Rumus SMA, EMA, Bollinger, dan RSI dilengkapi; contoh QQQ menampilkan α50=0,03921569, %B=−0,22, RSI 35,00, serta MACD 1,525/6,167/−4,642.
6. Overlay dijelaskan berskala log dan small multiples bersumbu y linear bersama.
7. Ringkasan metode dibagi menjadi dua tabel yang mencakup seluruh metode.
8. Rujukan Invesco dan Nasdaq diberi hyperlink aktif dengan label sumber dan tanggal akses.
9. Catatan generik dihapus dan diganti pertanyaan diskusi bertopik dengan angka; tanda titik ganda dirapikan.
10. Slide “Istilah penting” memperkenalkan padanan Indonesia untuk istilah utama.
11. Angka persentase pada teks/tabel ditulis memakai tanda % dan koma desimal.
12. Catatan slide perusahaan menyatakan bahwa deskripsi bisnis adalah ringkasan umum.
