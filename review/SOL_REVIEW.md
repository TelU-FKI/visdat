# Review independen — QQQ-Time-Series.pptx

## Ringkasan dan vonis

**Vonis: Layak dengan perbaikan; secara umum BAGUS untuk mahasiswa S1.** Deck 44 slide ini mengikuti identitas visual contoh dosen 24 slide dan memperluas cakupan metode dengan definisi, pembacaan kasus QQQ, penggunaan, serta keterbatasan. Hitung ulang terhadap CSV membenarkan angka keuangan utama, rumus indikator di kode, dan tabel data yang tampil. Namun, penyajian bulan Oktober 2026 yang belum selesai serta penyebutan jumlah tahun pada plot musiman berpotensi menghasilkan interpretasi yang salah. Rumus beberapa metode belum lengkap untuk diajarkan, dan label angka pada grafik tertentu terlalu kecil untuk ruang kelas.

## Lingkup pemeriksaan dan hasil mekanis

Saya membuka `SPEC.md`, `deck_numbers.md`, seluruh CSV dan `ASOF.txt`, kode `src/charts/`, kedua PPTX, serta hasil render PDF/JPEG pada `review/render/`. Deck berukuran 16:9, 44 slide, dengan 22 gambar (semua memiliki `descr`/alt text), 30 slide bercatatan pembicara, dan 21 catatan mengulang kalimat generik seperti “Bandingkan pola pada gambar ...” atau “Perhatikan label ...”. Median teks yang dapat diekstrak ialah 354 karakter per slide termasuk tabel; slide 3 mencapai 676 karakter dan 5 paragraf isi, slide 7 529 karakter dan 5 paragraf isi, sedangkan tabel slide 13 memiliki 43 sel terisi. Tidak ditemukan lebih dari 6 butir isi pada satu slide; tabel memang lebih panjang dari batas butir. Render visual seluruh 44 slide tidak menunjukkan teks terpotong atau objek bertumpuk; pola teks dan gambar yang berdampingan pada slide 18–22 serta 31–41 konsisten dengan pendekatan contoh dosen, meskipun contoh dosen hanya 24 slide.

### Audit angka dari data lokal

| Lokasi | Hasil hitung ulang | Penilaian |
|---|---:|---|
| Slide 6, `data/ASOF.txt` | Expense ratio 0,18%; tanggal unduh 19 Okt 2026 | Cocok dengan ASOF dan [Invesco QQQ](https://www.invesco.com/us/en/financial-products/etfs/invesco-qqq-trust-series-1.html). |
| Slide 9–11 | Total 10 holding 46,69179% → 46,69%; contoh NVDA 8,32742% → 8,33%, AAPL 7,3533505% → 7,35%; Teknologi 60,330003%, Layanan Komunikasi 12,59%, Konsumsi Siklikal 10,07% | Cocok; jumlah sektor CSV 100,020003% akibat pembulatan sumber. |
| Slide 12–14, 44 | 1.255 observasi, 18 Okt 2021–16 Okt 2026, tutup terakhir USD 709,79999 → 709,80; lima baris OHLCV slide 13 cocok setelah pembulatan | Cocok. |
| Slide 22 | Terbaik Apr 2026 +15,690079%; terburuk Apr 2022 −13,595743% | Cocok setelah pembulatan. |
| Slide 28–29 | GOOGL–GOOG 0,9972495; AAPL–MU 0,3095649 (pasangan minimum); QQQ–NVDA 0,7815914 | Cocok; gambar membulatkan ke dua desimal. |
| Slide 34 | R² linear 0,8488869; kubik 0,9480706; eksponensial 0,8953840 | Cocok pada skala harga setelah pembulatan. |
| Slide 35–37 | STL log harga akhir bulan `period=12`, `seasonal=99`: tren 5,682285–6,607310; musiman −0,036040–0,029294; residual −0,129053–0,088017, simpangan baku 0,046089; profil Jan–Des setelah ×100: 0,51; −1,35; −2,04; −3,60; 1,47; 2,07; 2,93; 1,57; −0,96; −2,32; 1,62; 0,10 | Cocok dengan angka slide/catatan dan gambar setelah pembulatan. |
| Slide 38–41 | Volatilitas 21 hari 18,0363% tahunan; drawdown minimum −35,6172% pada 28 Des 2022; RSI Wilder(14) 35,00475; MACD 1,524827, sinyal 6,166781, histogram −4,641954 | Cocok setelah pembulatan. |

Rumus pada slide 14, 31–33, 38–41 diperiksa terhadap `src/charts/`: return memakai `pct_change`; SMA memakai `rolling(n).mean`; EMA memakai `ewm(span=n, adjust=False)` sehingga α=2/(n+1); Bollinger memakai rata-rata 20 hari ±2 simpangan baku sampel (`ddof=1`); volatilitas memakai simpangan baku 21 return ×√252; RSI menginisialisasi rata-rata 14 perubahan lalu memperbarui dengan faktor Wilder; dan MACD memakai EMA 12/26 serta sinyal EMA 9. Perhitungan ulang ini memverifikasi konsistensi **terhadap berkas lokal**, bukan keaslian unduhan Yahoo/holdings pada tanggal tertentu.

## Temuan

### MAJOR — plot musiman salah menyebut jumlah tahun

**Slide 21; `src/charts/fig_a_04_seasonal_plot.py:12-18`.** Teks menyatakan “lima tahun yang tersedia”, tetapi kode menggambar enam garis berlabel 2021, 2022, 2023, 2024, 2025, dan 2026. Seri 2021 dimulai 18 Oktober, sedangkan 2026 berhenti 16 Oktober; hanya 2022–2025 adalah tahun kalender lengkap. **Perbaikan:** sebut “enam tahun kalender, dua di antaranya parsial”, bedakan garis/marker tahun parsial, dan tulis rentang data jelas pada slide, bukan hanya catatan kecil di gambar.

### MAJOR — bulan parsial diperlakukan sebagai observasi akhir bulan

**Slide 22–23, 35–37; `src/charts/fig_a_05_heatmap_bulanan.py:11-15`, `src/charts/fig_b_dekomposisi.py:17-20`.** Data terakhir adalah 16 Okt 2026, tetapi resampling `ME` menandai tutup 16 Okt sebagai **31 Okt 2026**; heatmap bulanan memuat return Oktober sementara −4,0513% tanpa penanda parsial. STL memakai 61 titik bulanan termasuk Oktober 2021 dan Oktober 2026 yang tidak lengkap, lalu slide 37 memperlihatkan profil sebagai seolah bulan kalender yang setara; jika Oktober 2026 dikeluarkan, rerata komponen musiman Oktober berubah dari sekitar −2,32% ke −2,00% (model dipasang ulang). Kalender slide 23 juga mencakup Oktober 2026 tetapi tidak menyebut bahwa bulan terakhir baru sampai tanggal 16. **Perbaikan:** buang bulan ujung yang tidak lengkap dari heatmap bulanan dan STL/profil, atau beri label “parsial s.d. 16 Okt” serta jelaskan konsekuensinya; untuk kalender, cukup beri label parsial. Perbarui angka profil setelah regenerasi.

### MAJOR — definisi fitting tidak sesuai model eksponensial

**Slide 34; `src/charts/fig_b_fitting.py:12-20`.** Slide mengatakan fitting “meminimalkan selisih kuadrat antara harga teramati dan nilai model” untuk ketiga fungsi, tetapi model eksponensial dipasang dengan `np.polyfit(x, np.log(y), 1)`: yang diminimalkan ialah kuadrat selisih pada **log harga**, lalu R² dievaluasi lagi pada harga asli (0,8954). **Perbaikan:** jelaskan pembedaan fungsi objektif ini pada slide/catatan, atau pasang model eksponensial dengan kuadrat galat harga agar definisi umum berlaku; hitung ulang R² jika model diubah.

### MAJOR — rumus pengajaran beberapa indikator tidak lengkap

**Slide 31–33, 40; `src/charts/fig_b_ema_vs_sma.py:14-15`, `src/charts/fig_b_bollinger.py:14-17`, `src/charts/fig_b_rsi.py:10-22`.** SMA ditulis `ΣPₜ₋ᵢ/n` tanpa batas penjumlahan `i=0…n−1`; slide EMA tidak menulis α=2/(n+1) meskipun diminta `SPEC.md` dan dipakai kode; slide Bollinger menyebut panel `%B` tanpa mendefinisikan `(P−pita bawah)/(pita atas−pita bawah)`; slide RSI hanya menyebut perbandingan rata-rata tanpa rumus RSI atau sifat pemulusan Wilder. Mahasiswa belum dapat mereproduksi gambar dari penjelasan slide saja. **Perbaikan:** tambahkan satu baris rumus kecil yang tetap terbaca per metode dan contoh interpretasi satu titik QQQ; bila ruang habis, pisahkan penjelasan formula dari gambar seperti pola contoh dosen.

### MINOR — skala log overlay dibandingkan dengan panel linear tanpa pengantar

**Slide 24, 26–27; `src/charts/fig_a_07_multi_overlay.py:15-16`, `src/charts/fig_a_08_multi_small.py:13-16`.** Overlay di slide 26 memakai `semilogy`/skala log, sedangkan small multiples slide 27 memakai sumbu y linear bersama. Label gambar 26 menyebut skala log, tetapi slide 24 tidak menjelaskan efeknya; mahasiswa bisa menganggap kedua gambar berskala sama karena memakai data indeks awal 100. **Perbaikan:** tambahkan kalimat bahwa jarak vertikal pada overlay merepresentasikan perubahan relatif, atau samakan skala kedua gambar dan jelaskan alasan pilihan tersebut.

### MINOR — angka pada beberapa gambar terlalu kecil saat diproyeksikan

**Slide 11, 18–23, 29, 36, 40–41; `src/charts/common.py:38-50`, `src/charts/fig_a_09_korelasi.py:19-23`.** Grafik dibuat dengan huruf dasar 9 pt, anotasi korelasi 6 pt, lalu beberapa gambar 8 inci diperkecil menjadi 6,45 inci di slide (sekitar 81% ukuran). Pada render slide 29, matriks 11×11 dan angka per sel hanya menempati bagian tengah slide; pada slide 23 nama hari dan sel kalender juga tampak kecil. **Perbaikan:** besarkan gambar/plot, gunakan font grafik lebih besar, ringkas matriks menjadi segitiga atau sorot hanya pasangan penting, dan proyeksikan render pada ukuran kelas untuk uji baca.

### MINOR — ringkasan metode melewatkan tiga metode yang sudah diajarkan

**Slide 42.** Tabel hanya merangkum line/area, candlestick, heatmap/seasonal, SMA/EMA, Bollinger, RSI/MACD; fitting, STL, volatilitas, drawdown, normalisasi, dan korelasi tidak punya baris meski menjadi inti slide 24–41. **Perbaikan:** lanjutkan tabel ke slide kedua atau kelompokkan dengan baris yang benar benar mewakili semua metode dan satu keterbatasan masing masing.

### MINOR — referensi dan klaim eksternal sulit dilacak

**Slide 6, 8, 44.** Identitas QQQ, Maret 1999, rasio 0,18%, dan definisi/bobot Nasdaq-100 sesuai [halaman resmi Invesco](https://www.invesco.com/us/en/financial-products/etfs/invesco-qqq-trust-series-1.html) dan [metodologi resmi Nasdaq yang berlaku Mei 2026](https://indexes.nasdaqomx.com/docs/Methodology_NDX_Effective_May_1_2026.pdf). Akan tetapi slide 44 hanya menulis “Halaman resmi Invesco QQQ dan Nasdaq-100” tanpa judul, tanggal akses, atau tautan spesifik; sumber klaim kategori Yahoo 0,19% juga hanya dapat ditemukan lewat CSV/ASOF, bukan rujukan di slide. **Perbaikan:** tambahkan URL/hyperlink aktif serta tanggal akses untuk dua laman resmi dan sebut berkas CSV serta tanggal ASOF untuk angka komposisi. Klaim rinci bahwa semua perusahaan holding menjalankan kegiatan yang dijelaskan di slide 7 tidak saya verifikasi satu per satu; **dugaan** fakta umumnya benar, tetapi sumber per perusahaan perlu ditambahkan bila slide itu dipertahankan.

### MINOR — catatan pembicara repetitif dan kurang membantu pengajaran

**Slide 10–11, 14, 18–22, 26–27, 29, 31–34, 37–41.** Pada 21 slide ditemukan dua kali pengulangan kalimat generik “Bandingkan pola pada gambar ...” atau “Perhatikan label ...” setelah catatan khusus; contohnya slide 10 bahkan mengulang “Perhatikan label ...” dua kali. **Perbaikan:** hapus duplikasi dan isi catatan dengan pertanyaan diskusi atau interpretasi angka spesifik, misalnya mengapa AAPL–MU 0,310 jauh di bawah GOOGL–GOOG 0,997.

### NIT — konsistensi istilah, gaya angka, dan penulisan

**Slide 6–7, 14, 24, 31–35, 42; catatan slide 10–11.** “Holding”, “overlay”, “small multiples”, “fitting”, “noise”, “lag”, “return”, “expense ratio”, dan “time series” bercampur dengan istilah Indonesia tanpa glosarium; istilah asing pada metode boleh dipertahankan, tetapi padanan pertama perlu diperkenalkan. Slide 6 memakai “0,18 persen”, sedangkan tabel memakai “0,18%”; slide 10–11 memiliki titik ganda `..` dalam catatan pembicara. **Perbaikan:** tetapkan padanan pada sebutan pertama (misalnya imbal hasil/return, kepemilikan/holding, pemulusan/smoothing), gunakan `%` atau “persen” secara konsisten, dan rapikan tanda baca catatan.

### NIT — profil STL berupa angka tetap dalam kode

**Slide 37; `src/charts/fig_b_dekomposisi.py:11,39-57`.** Dua belas angka `PROFILE_PERCENT` ditulis tetap; pemeriksaan saat ini menunjukkan semuanya cocok dengan hasil STL setelah pembulatan satu desimal, tetapi regenerasi setelah data diperbarui dapat menghasilkan gambar profil yang basi. **Perbaikan:** hitung profil langsung dari `result.seasonal.groupby(month).mean()*100` yang sama dengan slide 36.

## Kesimpulan pengajaran

Alur dari ETF, struktur OHLCV, jenis grafik, pemulusan, sampai indikator pasar sudah kuat dan lebih kaya daripada contoh dosen; slide 3–11 memberi konteks QQQ yang cukup bagi mahasiswa tanpa latar pasar modal. Fokus revisi sebaiknya pada label data parsial, ketepatan jumlah tahun, kecocokan penjelasan fitting, kelengkapan rumus, dan keterbacaan grafik, kemudian catatan pembicara dan referensi. Tidak ada temuan **BLOCKER** yang menuntut pembatalan materi, tetapi temuan **MAJOR** perlu selesai sebelum kelas.
