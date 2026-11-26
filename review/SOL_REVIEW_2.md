# Review independen putaran 2 — QQQ-Time-Series.pptx

## Vonis

**Layak dengan perbaikan.** Deck kini berisi 47 slide dan hampir semua koreksi putaran pertama terbukti pada slide, gambar, kode, dan hasil hitung ulang, sehingga materi secara umum baik untuk S1. Angka baru untuk 60 penutupan bulanan, 59 return bulanan, SMA, EMA, Bollinger, RSI, dan MACD cocok dengan CSV lokal. Namun slide 35 sekarang menyatakan tiga R² tidak sepenuhnya sebanding padahal semuanya dihitung dengan ukuran galat harga yang sama. Slide 24 juga membawa keterangan 2021 dari grafik lain ke kalender yang hanya berisi Nov 2025–Okt 2026, sementara sebagian angka di grafik masih kecil saat diproyeksikan.

## Pemeriksaan ulang setiap temuan putaran 1

| Temuan putaran 1 | Status | Bukti yang saya buka sendiri |
|---|---|---|
| Jumlah tahun dan tahun parsial plot musiman | **Tertutup** | Slide 22 menyebut enam tahun kalender, 2021 Nov–Des, 2026 Jan–Sep, serta empat tahun penuh 2022–2025; `src/charts/fig_a_04_seasonal_plot.py:14-29` membuang Okt 2026 dan memberi garis putus-putus pada tahun parsial. |
| Bulan parsial pada heatmap bulanan dan STL/profil | **Tertutup** | Slide 23 menandai Okt 2026 dikeluarkan, gambar kalender slide 24 menulis s.d. 16 Okt; `fig_a_05_heatmap_bulanan.py:12-22` menghapus titik terakhir dan `fig_b_dekomposisi.py:15-18,47-49` memakai 60 penutupan bulanan dan profil dari model yang sama. Catatan khusus: kalimat tentang 2021 pada slide kalender keliru (temuan baru). |
| Definisi fitting eksponensial | **Sebagian** | Slide 35 dan `fig_b_fitting.py:12-24` kini membedakan fitting harga linear/kubik dari fitting log harga eksponensial serta menyatakan R² dihitung pada harga. Penjelasan baru bahwa ketiga R² “tidak sepenuhnya sebanding” salah secara matematis (temuan baru). |
| Rumus SMA, EMA, Bollinger, RSI | **Tertutup** | Slide 32 mencantumkan batas `i=0` hingga `n−1`; slide 33 menulis α=2/(n+1); slide 34 menulis ±2s dan definisi %B; slide 41 menulis RS, pembaruan Wilder, dan RSI. Nilai contoh pada slide cocok dengan CSV (audit di bawah). |
| Log overlay versus sumbu linear small multiples | **Tertutup** | Grafik slide 27 berlabel skala log (`fig_a_07_multi_overlay.py:15-16`); catatan slide 27 menjelaskan jarak relatif. `fig_a_08_multi_small.py:15-25` memakai sumbu x/y bersama dan linear; catatan slide 28 menjelaskan mengapa sebagian garis tampak datar. |
| Keterbacaan angka pada gambar | **Sebagian** | Gambar penuh slide 27–28, 30, 37–38 membesar menjadi 9,4×5,29 inci dan `common.py:38-52` menaikkan huruf dasar menjadi 11 pt; `fig_a_09_korelasi.py:19-23` menaikkan angka sel menjadi 9 pt. Namun grafik berdampingan slide 22–23, 34–35, 39–42 masih selebar 6,45 inci; angka panel RSI/MACD, heatmap, dan legenda tetap kecil pada render `review/render2/contact-2.jpg` hingga `contact-4.jpg`. |
| Ringkasan metode tidak lengkap | **Tertutup** | Slide 43–44 sekarang merangkum grafik, musiman, normalisasi, korelasi, SMA/EMA, Bollinger, fitting, STL, volatilitas, drawdown, RSI, dan MACD. |
| Referensi dan hyperlink | **Sebagian** | Slide 47 memiliki 3 hyperlink aktif ke halaman [Invesco QQQ](https://www.invesco.com/us/en/financial-products/etfs/invesco-qqq-trust-series-1.html), [metodologi Nasdaq-100](https://indexes.nasdaqomx.com/docs/Methodology_NDX_Effective_May_1_2026.pdf), dan [ikhtisar Nasdaq-100](https://indexes.nasdaqomx.com/Index/Overview/NDX), semuanya dengan tanggal akses. Sumber bisnis setiap holding pada slide 8 belum diberikan; sebagian contoh telah saya cocokkan dengan sumber resmi, tetapi verifikasi lengkap sepuluh deskripsi masih **dugaan**. |
| Catatan pembicara generik/berulang | **Tertutup** | Pemeriksaan seluruh catatan menemukan 34 slide bercatatan dan **0** catatan berisi frasa generik berulang dari putaran 1; catatan slide 22, 27–28, 32–38 kini berisi pertanyaan spesifik. |
| Istilah, persen, tanda baca | **Tertutup** | Slide 3 memberi padanan istilah, slide 7–12 dan tabel slide 10 memakai tanda `%` dengan koma desimal; catatan slide 11 tidak lagi mengandung `..`. Istilah teknis asing yang dipertahankan telah diberi konteks. |
| Profil STL ditulis tetap | **Tertutup** | `src/charts/fig_b_dekomposisi.py:47-49` menghitung profil langsung dari `result.seasonal.groupby(month).mean()*100`, tanpa daftar angka tetap. |

## Audit angka independen

Saya menghitung dari `data/qqq_ohlcv.csv` dengan Python 3.13 pada lingkungan `py313`, tanpa menggunakan nilai di `deck_numbers.md` sebagai input. CSV memuat 1.255 harga dari 18 Okt 2021 hingga 16 Okt 2026, dengan harga akhir 709,799988 USD; 10 holding pertama berjumlah 46,69179%, teknologi 60,330003%, komunikasi 12,59%, konsumsi siklikal 10,07%, dan sampel lima baris OHLCV slide 14 cocok setelah pembulatan. Korelasi yang tetap tampil pada slide 29–30 juga cocok: GOOGL–GOOG 0,9972495; AAPL–MU 0,3095649; QQQ–NVDA 0,7815914; R² slide 35 tetap 0,8488869, 0,9480706, 0,8953840.

| Angka yang berubah/baru, lokasi slide | Perhitungan ulang | Hasil |
|---|---:|---|
| 22–23, 36–38: penutupan bulanan lengkap | 60 titik, Okt 2021–Sep 2026; 59 return bulanan | Cocok; Okt 2026 parsial dibuang. |
| 23: ekstrem 59 return bulanan | Apr 2026 +15,690079%; Apr 2022 −13,595743% | Cocok dengan +15,69% dan −13,60%. |
| 36–37: STL log harga, `period=12`, `seasonal=99`, `seasonal_deg=0`, `robust=False` | Tren 5,682251–6,596293; musiman −0,036262–0,028384; residual −0,128356–0,084856; simpangan baku residual 0,046309 | Cocok setelah pembulatan pada slide/catatan. |
| 38: profil musiman Jan–Des, komponen log ×100 | +0,556; −1,318; −2,035; −3,626; +1,425; +2,002; +2,837; +1,456; −1,089; −1,997; +1,659; +0,130 | Cocok dengan label gambar satu desimal. |
| 32–34: harga akhir dan rata-rata | Tutup 709,8000; SMA20 742,5190; SMA50 726,7734; EMA50 727,9407 USD | Cocok. |
| 33: α EMA50 | 2/51 = 0,0392156863 | Cocok dengan ≈0,039. |
| 34: Bollinger(20,2s) dan %B | Pita bawah 719,8486; atas 765,1894; %B = −0,221624 | Cocok; harga akhir memang di bawah pita bawah. |
| 39–42: volatilitas, drawdown, RSI, MACD | Volatilitas 21 hari ×√252 = 18,0363%; drawdown −35,6172% pada 28 Des 2022; RSI Wilder 35,00475; MACD 1,524827, sinyal 6,166781, histogram −4,641954 | Cocok setelah pembulatan. |

Catatan metode: komponen STL pada slide 38 dikalikan 100 dari satuan log; ini pendekatan persentase, bukan transformasi tepat `100×(exp(komponen)−1)`. Pada amplitudo yang tampil perbedaannya kecil (misalnya −0,03626 log menjadi sekitar −3,56% eksak), tetapi label “komponen musiman (%)” sebaiknya dijelaskan bila mahasiswa diminta menafsirkan angka secara presisi.

## Integritas dan render

Saya membuka PDF hasil `soffice` dan seluruh 47 halaman JPEG melalui empat lembar kontak di `review/render2/`; tidak terlihat objek saling menumpuk, teks terpotong, atau judul isi lebih dari satu baris (judul sampul memang dibuat beberapa baris). Pemeriksaan OOXML dengan `python-pptx`/ZIP menemukan 47 slide, 22 gambar dengan **0 alt text kosong**, 3 hyperlink eksternal pada slide 47, 34 slide dengan catatan nonkosong, **0 placeholder/teks kosong**, **0 bentuk di luar kanvas**, dan **0 ukuran font eksplisit di bawah 14 pt di luar tabel**. Paket ZIP berisi 236 entri; uji CRC, parsing semua XML, dan penelusuran 90 berkas relasi menemukan **0** kegagalan atau target internal yatim. LibreOffice membuka deck dan menghasilkan PDF tanpa galat konversi. Angka di dalam PNG tidak termasuk audit font PPTX 14 pt; keterbacaannya dinilai dari render visual.

## Temuan baru

### MAJOR — pernyataan tentang perbandingan R² menyesatkan

**Slide 35; `src/charts/fig_b_fitting.py:18-20`.** Semua R² dihitung dengan rumus yang sama, `1−SSE_harga/SST_harga`, untuk harga dan sampel yang sama; karena itu angka 0,8489, 0,9481, dan 0,8954 **dapat dibandingkan sebagai kecocokan harga dalam sampel**, meski model eksponensial diestimasi pada log harga. Kalimat slide “Karena fungsi objektif berbeda, ketiga R² tidak sepenuhnya sebanding” dan baris ringkasan slide 44 “R² tak selalu sebanding” mengaburkan fakta ini. **Perbaikan:** tulis bahwa *proses fitting* memakai fungsi objektif berbeda, tetapi R² harga pada sampel sama tetap sebanding sebagai metrik deskriptif; tekankan bahwa kompleksitas model dan kecocokan dalam sampel tidak membuktikan kemampuan prediksi.

### MINOR — kalender memuat keterangan tahun yang tidak ada pada gambar

**Slide 24 dan catatan pembicaranya; `src/build_deck.py:430-436`; `src/charts/fig_a_06_heatmap_kalender.py:18-21`.** Teks bawah dan catatan slide mengatakan “2021 hanya memuat Nov–Des”, sedangkan kode memilih **12 bulan terakhir**, yaitu Nov 2025 sampai Okt 2026, seperti label pada gambar. Ini tampaknya terbawa dari penjelasan heatmap bulanan slide 23. **Perbaikan:** hapus klausa 2021 pada slide dan catatan; gunakan “Nov 2025–Okt 2026, dengan Okt 2026 hanya sampai tanggal 16”.

### MINOR — angka kecil pada gambar berdampingan masih membatasi pembacaan kelas

**Slide 22–23, 34–35, 39–42; `src/charts/common.py:38-52`.** Dasar font grafik 11 pt diperkecil bersama PNG 8 inci menjadi 6,45 inci pada beberapa slide, sehingga teks sumbu/legenda efektif sekitar 9 pt; panel %B, RSI, MACD dan sel heatmap tampak kecil pada render 90 dpi. Perbaikan putaran ini jelas membantu gambar penuh, tetapi belum sepenuhnya menutup temuan keterbacaan untuk slide teks+grafik. **Perbaikan:** besarkan gambar atau pisahkan gambar dari teks untuk metode yang memiliki dua panel; uji proyeksi dan targetkan label/angka grafik setara setidaknya 14 pt pada ukuran slide akhir.

### NIT — label persen komponen log perlu ketelitian istilah

**Slide 38; `src/charts/fig_b_dekomposisi.py:47-59`.** Angka batang diperoleh dari komponen STL pada **log harga ×100**, bukan perubahan harga persis dalam persen; untuk komponen minimum −0,036262, perubahan multiplicative tepatnya `100×(exp(−0,036262)−1)≈−3,56%`, sedangkan pendekatan log ialah −3,63%. **Perbaikan:** sebut “komponen log ×100 (≈%)” pada sumbu/catatan, atau transformasikan `exp(s)−1` sebelum menulis tanda persen.

## Fakta eksternal

Identitas QQQ, tanggal mulai Maret 1999, dan rasio biaya 0,18% di slide 7 sesuai [halaman produk Invesco](https://www.invesco.com/us/en/financial-products/etfs/invesco-qqq-trust-series-1.html); deskripsi dan metode bobot Nasdaq-100 di slide 9 sesuai [ikhtisar](https://indexes.nasdaqomx.com/Index/Overview/NDX) dan [metodologi resmi Nasdaq](https://indexes.nasdaqomx.com/docs/Methodology_NDX_Effective_May_1_2026.pdf). Deskripsi Micron dan AMD pada slide 8 sesuai [profil resmi Micron](https://www.micron.com/about/company/corporate-profile) dan [produk resmi AMD](https://www.amd.com/en/products.html); pasangan GOOGL/GOOG sesuai [laporan Alphabet](https://abc.xyz/assets/e1/31/38e9bf5540a2bf9a90221b96aa95/2022-alphabet-annual-report.pdf). Deskripsi bisnis holding lainnya belum diverifikasi satu per satu dan saya tandai sebagai **dugaan**, bukan kesalahan yang terbukti. Angka bobot holding dan sektor diverifikasi terhadap CSV lokal, bukan terhadap snapshot independen dari penyedia data.
