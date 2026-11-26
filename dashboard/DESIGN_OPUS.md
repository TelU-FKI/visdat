# DESAIN: "J.A.R.V.I.S. // IHSG 2026": dashboard teks berita IHSG

Dokumen konsep, bukan kode produksi. Target: Minggu-09 Visualisasi Data (word cloud / visualisasi teks), dipakai dosen di kelas lewat proyektor, dibuka offline dari `dashboard/index.html`.

Status data saat dokumen ditulis (uji cepat 9 Nov 2026, gabungan `data/news/cnbc_{A,B,C}.csv` + berkas acuan dosen, dedup per `url`): **1.895 artikel**, per bulan Jan 333, Feb 217, Mar 208, Apr 211, Mei 22-76 (angka naik di antara dua pengecekan, berarti pengumpulan masih berjalan), Jun 111, Jul 247, Agu 9, Sep 184, Okt 282, Nov (s.d. 9) 71. Median panjang isi 299 kata. Sebagian artikel Juli dan Agustus berisi `content` kosong (artikel video). Angka ini akan berubah; desain tidak boleh bergantung pada jumlah tertentu.

---

## 1. Konsep dan cerita data

**Satu kalimat:** layar HUD ala J.A.R.V.I.S. yang "memindai" sebelas bulan berita IHSG dan menunjukkan bahwa kata yang *paling sering* hampir tidak berubah, sedangkan kata yang *paling khas* tiap bulan menceritakan apa yang sebenarnya terjadi.

**Cerita yang ditonjolkan (busur Jan sampai Nov 2026):**
1. **Guncangan (Jan):** MSCI membekukan penilaian free float; IHSG anjlok sekitar 7% dan perdagangan dihentikan sementara (28 Jan). Kata khas bulan ini dari uji cepat: *msci, halt, kustodian, free float*.
2. **Geopolitik (Mar sampai Apr):** kata khas bergeser ke *israel, khamenei, tanker, blokade, gencatan senjata*. Pasar domestik dipengaruhi berita luar negeri.
3. **Tinjauan MSCI (Mei sampai Jun):** *review, classification, aksesibilitas*. Ini kelanjutan dari guncangan Januari.
4. **Asing dan suku bunga (Jul sampai Sep):** *asing, borong, net (sell/buy), rdg, destry, yield, treasury*.
5. **Regulasi dan AS (Okt sampai Nov):** *lot, pengetatan, penegakan, kevin warsh*, lalu *pemilu sela, kongres, demokrat, republik*.

ASUMSI: daftar di atas berasal dari skor kekhasan kasar (frekuensi dokumen × log rasio bulan) pada data yang belum lengkap. Pekerja 1 harus menghitung ulang daftarnya dan menulis teks naratif final di `events.json`, bukan menyalinnya dari dokumen ini.

Pelajaran inti bagi mahasiswa: **frekuensi mentah itu membosankan dan menyesatkan** (kata teratas setiap bulan selalu *gabungan, perdagangan, level, menjadi*). Cara pembobotan menentukan cerita yang muncul. Dashboard dibangun di sekitar satu tombol pembanding: **FREKUENSI dan KHAS**.

---

## 2. Tata letak 16:9 (acuan 1920×1080)

```
┌──────────────────────────────────────────────────────────────────────────────────────────┐
│ HEADER 56px  J.A.R.V.I.S.//IHSG-2026   [BULAN: JAN 2026  n=333]  [MODE: KHAS]   09:41 WIB │
├──────────────────┬──────────────────────────────────────────┬────────────────────────────┤
│ P2 PERINGKAT     │                                          │ P3 JARINGAN KATA           │
│ (bar 15 kata)    │        P1 BOLA KATA 3D (hero)            │ (ko-kemunculan, 2D)        │
│ 20% lebar        │        44% lebar, ~62% tinggi            │ 36% lebar, ~36% tinggi     │
│ batang + angka   │        80 kata, berputar pelan           │ ≤40 node, ≤90 sisi         │
│ "41% artikel"    │        reticle di tengah                 ├────────────────────────────┤
│                  │                                          │ P5 JUDUL TERSARING         │
│                  │                                          │ 5-6 judul tampak, gulir    │
│                  │                                          │ ~26% tinggi                │
├──────────────────┴──────────────────────────────┬───────────┴────────────────────────────┤
│ P4 GARIS WAKTU + HARGA ^JKSE (60% lebar, 30% t.)│ P6 BUMP CHART PERINGKAT (40% lebar)     │
│ trek atas: garis harga harian, anotasi 28 Jan   │ 10 kata × 11 bulan, garis peringkat     │
│ trek bawah: batang jumlah artikel per bulan     │ kata terpilih menyala, sisanya redup    │
│ ◄ penggeser bulan (brush) ►   [▶ AUTO]          │                                         │
└─────────────────────────────────────────────────┴─────────────────────────────────────────┘
```

**Hirarki visual:** (1) P1 bola kata: terbesar, satu-satunya elemen yang bergerak terus. (2) P4 garis waktu: kontrol utama dan konteks harga. (3) P2 dan P3: penjelasan dari "kata apa" dan "berhubungan dengan apa". (4) P5 dan P6: detail saat diminta. Header hanya untuk status, tidak dekoratif.

Grid CSS: `grid-template-columns: 20fr 44fr 36fr; grid-template-rows: 56px 62fr 30fr;` dengan jarak antarpanel 12px. Di bawah lebar 1280px, P6 pindah ke tab di dalam P4 (proyektor kelas yang 1280×800 tetap aman). ASUMSI: proyektor kelas minimal 1280×720.

---

## 3. Visualisasi (6 panel)

Semua panel membaca satu state global: `{month, mode, term}`. `month` berisi `"2026-01"` sampai `"2026-11"` atau `"ALL"`, `mode` berisi `"freq"` atau `"khas"`, `term` berisi id kata atau `null`.

### P1 Bola kata 3D (hero)
- **Data:** `terms[month][mode]`, 80 kata teratas: `label`, `score`, `df_share`, `cat` (istilah / entitas / kode saham).
- **Render:** modul sendiri berbasis DOM (`<button>` per kata, `transform: translate3d() scale()`), posisi di bola Fibonacci, satu loop `requestAnimationFrame`. Polanya meniru TagCloud.js, tetapi ditulis sendiri karena butuh ukuran per kata, warna per kategori, morph antarbulan, dan sorotan. Tidak memakai three.js; teks DOM tetap tajam di proyektor dan bisa difokus dengan keyboard.
- **Encoding:** ukuran huruf ~ √skor (18-56px), warna = kategori, opasitas 0,35-1 menurut kedalaman z.
- **Animasi:** rotasi 0,08 rad/detik di sumbu Y. Saat bulan berganti, kata yang tetap ada meluncur ke posisi barunya, kata baru membesar dari 0, kata yang hilang mengecil (600ms, GSAP).
- **Interaksi:** seret untuk memutar, hover menghentikan rotasi dan memunculkan tooltip ("muncul di 137 dari 333 artikel"), klik memilih `term`.
- **Pedagogi:** bola ini sengaja dipasangkan dengan P2. Di 3D, kata di belakang tampak kecil dan pudar walaupun skornya tinggi, jadi **perspektif merusak encoding ukuran**. Mahasiswa diminta menebak kata nomor 3 dari bola, lalu mencocokkannya dengan P2. Daya tarik visual dan ketepatan baca adalah pertukaran yang bisa diukur.

### P2 Peringkat kata (pasangan "jujur")
- **Data:** 15 kata teratas dari daftar yang sama dengan P1.
- **Render:** D3 SVG, batang horizontal, label kiri 20px, nilai di ujung batang (`41%` untuk mode frekuensi, `0,83` untuk mode khas).
- **Animasi:** batang menyusun ulang dengan transisi `y` 500ms (pola bar chart race).
- **Interaksi:** klik batang = pilih `term`. Batang terpilih berwarna amber.
- **Pedagogi:** posisi pada skala bersama dibaca jauh lebih tepat daripada ukuran huruf (Cleveland & McGill). Panel ini juga paling jelas menampilkan perbedaan mode FREKUENSI dan KHAS.

### P3 Jaringan ko-kemunculan
- **Data:** `cooc[month]`: ≤40 node, ≤90 sisi, bobot NPMI (lihat §7).
- **Render:** `force-graph` (2D canvas, vasturiano). Ukuran node ~ df, tebal sisi ~ NPMI, label selalu tampil untuk 15 node terbesar dan muncul saat hover untuk sisanya.
- **Animasi:** simulasi berjalan 120 tick (`cooldownTicks`), lalu dibekukan. Ganti bulan = node yang sama mempertahankan posisi (`fx/fy` lama sebagai titik awal), sehingga struktur tidak "meledak" tiap bulan.
- **Interaksi:** klik node = pilih `term` dan menyorot tetangganya (yang lain diredupkan menjadi 15%). Seret node diperbolehkan.
- **Pedagogi:** dari kata ke hubungan antarkata. Kata "asing" di Juli terhubung dengan "borong" dan "net buy", di Jan dengan "jual" dan "msci". Konteks mengubah makna. Panel ini juga mengajarkan pemangkasan jaringan: graf yang tidak dipangkas adalah hairball.

### P4 Garis waktu + harga ^JKSE (pengendali utama)
- **Data:** `prices` (penutupan harian), `months[].n` (jumlah artikel), `events` (≤6 anotasi).
- **Render:** D3 SVG, dua trek dengan sumbu-x waktu yang sama. Trek atas: garis harga dan pita bulan terpilih. Trek bawah: batang jumlah artikel per bulan; bulan dengan n<50 diberi arsiran dan label `DATA TIPIS`.
- **Animasi:** pita sorot meluncur ke bulan baru (400ms). Saat intro, garis harga digambar dari kiri ke kanan (`stroke-dashoffset`).
- **Interaksi:** klik atau seret penggeser = ganti `month`. Tombol ▶ AUTO. Klik penanda peristiwa = lompat ke bulannya dan memilih kata terkait. Bila `term` dipilih, trek bawah berganti menjadi "jumlah artikel per bulan yang memuat *term*" (garis amber).
- **Pedagogi:** visualisasi teks butuh sumbu waktu dan konteks numerik. Juga peringatan eksplisit di keterangan panel: *"Kemunculan kata dan harga berbarengan dalam waktu, bukan bukti sebab-akibat."*

### P5 Judul tersaring
- **Data:** `headlines` (judul, tanggal, url, tag CNBC, id kata yang muncul). **Tanpa isi artikel.**
- **Render:** daftar DOM. Judul 20px, tanggal mono 16px, kata terpilih di dalam judul disorot amber. Maksimal 50 baris di DOM (sisanya "+212 lagi").
- **Interaksi:** tersaring oleh `month` ∩ `term`. Klik judul membuka URL CNBC di tab baru (satu-satunya tautan eksternal, dan hanya saat diklik). Tanpa `term`, panel menampilkan 8 judul terbaru bulan itu.
- **Pedagogi:** *close reading* setelah *distant reading*. Mahasiswa memeriksa apakah kata dari model benar-benar berarti hal yang kita kira.

### P6 Bump chart peringkat
- **Data:** `bump`: 12 kata dengan peringkat khas tertinggi gabungan semua bulan, peringkat 1-20 per bulan (`null` jika di luar 20).
- **Render:** D3 SVG, garis peringkat, titik per bulan, label kata di ujung kanan.
- **Interaksi:** hover garis = sorot; klik = pilih `term`. Bulan aktif ditandai garis vertikal.
- **Pedagogi:** ringkasan seluruh busur dalam satu gambar statis, jawaban untuk "kata apa yang mendominasi tiap bulan" tanpa perlu memutar animasi. Ini juga mengajarkan bahwa animasi (P1) buruk untuk perbandingan lintas waktu, sedangkan *small multiples* atau *bump* lebih baik.

Dipertimbangkan lalu dibuang dari daftar panel: partikel latar (tsParticles), radar/gauge dekoratif, awan kata 2D datar terpisah (sudah tercakup oleh P1 dan P2).

---

## 4. Bahasa desain

### Palet (mode gelap, dioptimalkan untuk proyektor)
| Token | Hex | Pakai | Kontras vs `--bg` |
|---|---|---|---|
| `--bg` | `#05080D` | latar halaman | - |
| `--panel` | `#0A1520` | isi panel | - |
| `--line` | `#1F5A6E` | bingkai, grid | dekoratif |
| `--cyan` | `#3FE0FF` | aksen utama, kata kategori istilah, garis harga | ≈13:1 |
| `--text` | `#E6F7FF` | teks utama | ≈18:1 |
| `--muted` | `#7FA3B5` | label sekunder, sumbu | ≈7,4:1 |
| `--amber` | `#FFB238` | **hanya** untuk seleksi/sorot | ≈11:1 |
| `--violet` | `#B49CFF` | kategori entitas (MSCI, BI, The Fed) | ≈8:1 |
| `--mint` | `#3DDC97` | kode saham; harga naik ▲ | ≈10:1 |
| `--red` | `#FF4D5E` | harga turun ▼, penanda 28 Jan | ≈6:1 |

Aturan: merah/hijau selalu disertai glif ▲▼ (aman buta warna). Amber dicadangkan untuk "yang sedang dipilih" agar mata langsung menemukannya. Kontras dihitung manual dari luminans relatif; Pekerja 2 memverifikasinya dengan alat kontras. Proyektor menaikkan level hitam dan memudarkan saturasi, jadi garis tipis <1,5px dan warna gelap di bawah `#1F5A6E` tidak dipakai untuk informasi.

### Tipografi (ditanam lokal di `dashboard/vendor/fonts/`, woff2, lisensi OFL)
- **Chakra Petch** (400/600): judul panel (huruf kapital, letter-spacing 0,12em), label, judul berita. Bentuknya bersudut sehingga terasa "teknis", tetapi masih terbaca di 18px.
- **JetBrains Mono** (400/700): semua angka (`font-variant-numeric: tabular-nums`), jam, n artikel, harga.
- Orbitron ditolak: terlalu lebar dan sulit dibaca di bawah 24px.
- Ukuran minimum di 1080p: label 18px, isi 20px, judul panel 22px, angka KPI header 28px. Patokan: dari baris belakang kelas (~10 m), tulisan 18px di layar 2,5 m masih terbaca. ASUMSI: ukuran layar dan jarak kelas belum diukur; uji di ruang kelas sebelum dipakai.

### Motif HUD (dengan batas)
- **Bingkai panel:** sudut terpotong 12px (`clip-path: polygon`) dan penanda sudut "L" 16px warna cyan. Tidak ada bingkai ganda.
- **Reticle:** satu saja, di tengah P1: dua lingkaran putus-putus dan 4 tick, berputar 1 putaran/60 detik, opasitas 0,25.
- **Scanline:** overlay statis `repeating-linear-gradient` 3px, opasitas **0,04**, `pointer-events:none`. Tidak dianimasikan kecuali satu kali sapuan saat intro.
- **Glow:** `text-shadow 0 0 8px` hanya pada judul panel, angka header, dan kata terpilih. **Dilarang** pada 80 kata bola yang bergerak (mahal dan membuat teks blur di proyektor).
- **Grid latar:** garis 1px `--line` opasitas 0,15 tiap 48px, statis.
- **Batas keras:** maksimal 1 elemen dekoratif bergerak per panel; tidak ada teks dekoratif palsu (heksadesimal acak, "SYSTEM ONLINE" berulang); setiap angka di layar adalah data nyata.

---

## 5. Animasi

### Intro "boot sequence" (6,5 detik; tombol Enter/Esc atau klik untuk melewati)
| t (detik) | Peristiwa |
|---|---|
| 0,0-0,6 | Layar hitam, satu garis cyan horizontal melebar dari tengah (scaleX 0 ke 1). |
| 0,6-1,4 | Bingkai 6 panel "dirakit": sudut L muncul berurutan (stagger 80ms), garis bingkai digambar (`stroke-dashoffset`). |
| 1,4-2,4 | Header mengetik: `J.A.R.V.I.S. // IHSG-2026 :: MEMUAT 1.895 ARTIKEL`; angka menghitung naik dari 0 (data nyata dari `meta`). |
| 2,4-3,6 | P4: garis harga Jan-Nov tergambar kiri ke kanan; batang jumlah artikel tumbuh. |
| 3,6-4,4 | Penanda 28 Jan berkedip merah 2×; label "MSCI: free float dibekukan, trading halt". |
| 4,4-5,6 | P1: 80 kata Januari terbang dari tepi menuju posisi bola; reticle menyala. P2 batang tumbuh. |
| 5,6-6,5 | P3 jaringan mengendap, P6 garis bump tergambar, sapuan scanline sekali, status `SIAP`. |

Implementasi: satu `gsap.timeline()`; setiap panel mengekspos `introIn(tl, at)` sehingga urutan diatur di satu tempat.

### Transisi antarbulan (total ≤700ms, semua panel serentak)
P4 pita meluncur 400ms → P2 batang menyusun ulang 500ms → P1 morph kata 600ms → P3 node pindah/masuk/keluar 600ms → P5 daftar crossfade 200ms → P6 garis vertikal geser 300ms. Easing `power2.out`. Bila tombol ditekan saat transisi berjalan, transisi lama di-`kill()` dan langsung lompat ke target (tidak ada antrean).

### Hover dan klik
Hover: kata membesar 1,15×, tooltip muncul 120ms. Klik memilih: amber di semua panel dalam ≤100ms, panel lain meredup ke 35% kecuali yang terkait. Klik kosong atau Esc = batal pilih.

### `prefers-reduced-motion: reduce`
Intro diganti fade-in 400ms. Bola tidak berputar otomatis (masih bisa diseret); transisi menjadi crossfade 150ms; reticle dan scanline statis; penggeser AUTO tetap berfungsi tetapi tanpa morph. Juga bisa dipaksa lewat tombol `?motion=0` di URL.

### Anggaran performa (target 60 fps, minimal median 55 fps)
- P1: 80 elemen DOM, hanya `transform` dan `opacity` yang diubah per frame; tanpa `filter`/`text-shadow` bergerak.
- P3: ≤40 node, ≤90 sisi, simulasi dibekukan setelah 120 tick, jadi 0 biaya per frame saat diam (`autoPauseRedraw`).
- P4/P2/P6: SVG statis di antara transisi.
- Hanya satu loop rAF aktif (P1); loop berhenti saat tab tersembunyi (`visibilitychange`).
- ASUMSI perangkat: "laptop biasa" = Intel i5 gen-10 atau Apple M1 dengan GPU terintegrasi, Chrome/Edge terbaru.

---

## 6. Interaksi dan mode kelas

| Tombol | Aksi |
|---|---|
| ← / → | bulan sebelumnya / berikutnya (berhenti di Jan dan Nov) |
| Home | `ALL` (seluruh periode) |
| Spasi | putar otomatis (4 detik per bulan), tekan lagi untuk berhenti |
| M | ganti mode FREKUENSI dan KHAS |
| 1 sampai 6 | perbesar panel ke layar penuh (fokus penjelasan); Esc kembali |
| F | layar penuh browser (Fullscreen API) |
| R | reset: Jan, mode KHAS, tanpa pilihan, bola ke posisi awal |
| Esc | batal pilih kata / keluar dari panel diperbesar |
| ? | kartu bantuan pintasan (overlay) |

Semua kontrol juga punya tombol di header (untuk dosen yang memakai clicker/mouse). Kontrol keyboard tidak aktif saat fokus ada di input.

**Mode presentasi (F):** header mengecil ke 40px, kursor hilang setelah 3 detik diam, semua ukuran huruf dinaikkan 1 tingkat (`--scale: 1.12`).

**Tips mengajar per panel (urutan sesi ±25 menit):**
1. *Mulai dari P1, mode FREKUENSI.* Tanya kelas: "Apa yang terjadi di Januari?" Jawabannya tidak bisa didapat: hanya *gabungan, perdagangan, level*. Tekan **M**: *msci, halt* muncul. Bahas stopword domain dan TF-IDF.
2. *P1 lawan P2.* Minta mahasiswa menunjuk kata peringkat ke-3 di bola, lalu tunjukkan P2. Bahas efek perspektif dan bahwa ukuran huruf dipengaruhi panjang kata.
3. *P4 + Spasi.* Putar otomatis Jan sampai Nov sambil diam; minta kelas mencatat 1 kata per bulan. Bandingkan catatan dengan P6.
4. *P3.* Klik "asing" di Jan lalu di Jul; tetangganya berubah. Bahas ko-kemunculan dan pemangkasan (tunjukkan angka "dari 4.812 pasangan, 90 ditampilkan" di pojok panel).
5. *P5.* Klik sebuah kata dan baca 2 judul. Apakah maknanya sesuai? Ini validasi manusia.
6. *Penutup di P4:* "Berita negatif berbarengan dengan harga turun. Apakah berita menyebabkan harga turun, atau sebaliknya?"

---

## 7. Pipeline data (Python, `~/miniconda3/envs/py313/bin/python`)

### Masukan
`data/news/cnbc_{A,B,C}.csv` + berkas acuan dosen (`cnbc_ihsg_articles_clean.csv`, hanya dibaca). Dedup `url`. Filter `publish_date` 2026-01-01..2026-11-09. Artikel dengan `content` kosong/`nan` tetap dipakai tetapi teksnya hanya judul + keywords, dan jumlahnya dilaporkan.

### Keluaran (`dashboard/data/`)
JSON untuk diperiksa manusia dan diuji, **ditambah `data.js`** yang membungkus semuanya sebagai `window.IHSG_DATA = {...}`. Alasan: `fetch()` ke file JSON lokal diblokir Chrome di `file://`, sedangkan `<script src>` lokal boleh. Anggaran ukuran `data.js` ≤ 1,5 MB.

```text
meta.json      {generated_at, n_articles, n_empty_content, period:[start,end],
                months:[{id:"2026-01", label:"JAN", n:333, thin:false}], pipeline_version}
terms.json     {"2026-01": {"freq":[T...80], "khas":[T...80]}, ..., "ALL": {...}}
               T = {id:"msci", label:"MSCI", cat:"entity|term|ticker",
                    df:137, df_share:0.41, score:0.83, rank:1}
cooc.json      {"2026-01": {nodes:[{id,label,cat,df}], links:[{source,target,npmi,count}],
                            n_pairs_before_prune:4812}, ...}
bump.json      {months:[...11], terms:[{id,label,ranks:[1,3,null,...]}]}   // 12 kata
headlines.json [{i:0, d:"2026-01-28", t:"Mengenal MSCI, ...", u:"https://...",
                 k:["msci","ihsg"], m:"2026-01", terms:["msci","free_float",...]}]
prices.json    [{d:"2026-01-02", c:8123.4}] , source:"yfinance ^JKSE", fetched_at
events.json    [{d:"2026-01-28", label:"MSCI bekukan free float; trading halt",
                 term:"msci", headline_ids:[12,15]}]   // ≤6, ditulis tangan, tiap peristiwa wajib merujuk judul
```

`headlines.terms` hanya berisi id kata dari kosakata tampil (≤ ~600 id unik), bukan potongan isi. Itu turunan statistik, bukan teks artikel.

### Langkah pembersihan
1. **Buang boilerplate:** awalan `Jakarta, CNBC Indonesia -`, baris `Baca juga`, kredit foto/video, `(xxx/xxx)` inisial redaksi di akhir, URL, angka murni dan tanggal (angka tidak berguna di awan kata; level IHSG sudah ada di P4).
2. **Frasa sebelum tokenisasi:** gabungkan frasa dari (a) daftar `keywords_clean` CNBC yang muncul ≥5 kali dan terdiri dari 2-3 kata (mis. `free float`, `bank indonesia`, `the fed`, `net sell`, `gencatan senjata`, `pemilu sela`) dan (b) bigram berskor NPMI ≥0,5 dengan frekuensi ≥10 (`nltk.collocations`). Disimpan sebagai `free_float`, ditampilkan sebagai "free float".
3. **Kode saham:** token kapital 4 huruf yang cocok dengan daftar emiten (BBCA, BBRI, TLKM, ...) diberi `cat:"ticker"` dan tidak di-stem. ASUMSI: daftar emiten diambil dari tag CNBC dan pola `(XXXX)` dalam teks; tidak memakai sumber luar.
4. **Entitas:** kamus kecil buatan tangan (MSCI, BEI, OJK, BI, KSEI, The Fed, Danantara, Trump, Warsh, ...) diberi `cat:"entity"` dan ditampilkan dengan kapitalisasi aslinya.
5. **Huruf kecil, tokenisasi** `[a-z][a-z0-9]+`, panjang ≥3.
6. **Stopword (tiga lapis):** (a) daftar Sastrawi (`StopWordRemoverFactory`, sudah terpasang di py313); (b) **stopword domain**: `ihsg, indeks, harga, saham, gabungan, bursa, pasar, perdagangan, level, persen, rp, triliun, miliar, cnbc, indonesia, jakarta, hari, pekan, sesi, ditutup, dibuka, menjadi, sebesar, hingga, nilai`; (c) kata derau yang terlihat di uji cepat: `minor, tergolong, time, all, dulu, diri, nan, video`. Daftar (b) dan (c) disimpan di `src/dashboard/stopwords_domain.txt` dan wajib ditinjau manusia. Kata seperti *naik/turun/melemah/menguat* **tidak** dibuang (bermakna arah pasar), tetapi otomatis turun peringkat di mode KHAS.
7. **Kata dasar:** stemmer Sastrawi dipakai **hanya untuk pengelompokan** (mis. *melemah, pelemahan, lemah* menjadi `lemah`); label yang ditampilkan adalah **bentuk permukaan paling sering** dalam kelompok itu. Alasan: Sastrawi kadang memotong berlebihan (*perdagangan* menjadi *dagang*), sehingga label hasil stem terasa asing. Stem di-cache per token unik (13 ribu kosakata), bukan per kemunculan, karena Sastrawi lambat.

### Pemeringkatan kata
- **Unit hitung = dokumen (artikel), bukan kemunculan.** `df_share = artikel memuat kata / artikel bulan itu`. Satu artikel yang mengulang "MSCI" 20 kali tidak boleh mendominasi, dan normalisasi per bulan menetralkan jumlah artikel yang timpang (Agu 9 lawan Jan 333).
- **Mode FREKUENSI:** urut `df_share`. Ditampilkan apa adanya justru sebagai pembanding yang "membosankan".
- **Mode KHAS (bawaan):** gaya c-TF-IDF, dengan *bulan sebagai dokumen*: `score = df_share(w, m) × log(1 + M / Σ_m' [df_share(w,m') ≥ 0,05])`, M = jumlah bulan. Syarat: df ≥ max(3, 5% artikel bulan itu) supaya kata yang hanya muncul di satu artikel tidak menang.
- **Alasan memilih c-TF-IDF per bulan, bukan TF-IDF per artikel:** pertanyaan kita adalah "apa yang khas untuk bulan ini", jadi satuan pembandingnya adalah bulan. TF-IDF per artikel lalu dirata-rata cenderung mengangkat kata langka dari artikel panjang. Rumusnya juga cukup sederhana untuk ditulis di papan tulis.
- **Bulan tipis (n<50):** tetap dihitung, diberi `thin:true`, dan UI menampilkan peringatan. Ambang df minimum memakai 3 artikel.
- `ALL`: frekuensi = df_share seluruh korpus; khas = tidak berlaku, jadi P1 memakai frekuensi dengan stopword domain (tombol M dinonaktifkan dan diberi keterangan).

### Ko-kemunculan dan pemangkasan
- **Unit konteks = paragraf** (isi dipecah per baris baru; judul dihitung sebagai satu paragraf). Satu artikel 300 kata membuat hampir semua kata saling berhubungan, sedangkan paragraf lebih dekat dengan "dibicarakan bersama".
- **Kandidat node:** 60 kata teratas mode KHAS bulan itu, ditambah 10 kata teratas FREKUENSI yang bukan stopword (supaya ada "jangkar" yang dikenal).
- **Bobot:** NPMI antarpasangan di tingkat paragraf; simpan pasangan dengan `count ≥ 4` dan `npmi ≥ 0,1`.
- **Pemangkasan agar terbaca:** (1) tiap node menyimpan 3 sisi NPMI terbesar; (2) tambahkan *maximum spanning tree* (networkx) agar graf tetap terhubung; (3) potong ke ≤90 sisi menurut NPMI; (4) buang node tanpa sisi, lalu ambil ≤40 node berdasarkan df. Catat `n_pairs_before_prune` untuk ditampilkan di panel (bahan ajar).
- **Stabilitas tata letak:** praproses tidak menyimpan posisi; P3 meneruskan posisi node yang sama antarbulan di sisi klien.

### Harga
`src/dashboard/fetch_prices.py`: `yfinance.download("^JKSE", start="2026-01-01", end="2026-11-10")`, simpan cache `data/prices/jkse_2026.csv` (supaya bisa dibangun ulang offline) dan `prices.json`. ASUMSI: yfinance mengembalikan ^JKSE lengkap; level ~8.300 akhir Jan dan ~4.900-5.100 awal Nov **belum diverifikasi**. Pekerja 1 wajib mencocokkan harga 27-29 Jan dengan judul berita "anjlok 7%" sebelum anotasi dipakai. Jika unduhan gagal, P4 tetap tampil dengan trek artikel saja dan keterangan "harga tidak tersedia".

---

## 8. Risiko dan yang sengaja ditolak

**Risiko**
| Risiko | Penanganan |
|---|---|
| Data per bulan timpang/tidak lengkap (Agu 9, Mei masih bertambah) | `df_share` per bulan, label `DATA TIPIS`, n selalu tampil di header. Praproses dijalankan ulang setelah pengumpulan selesai. |
| Hasil KHAS menampilkan nama orang/derau (mis. *yudhi*) | stopword lapis (c) ditinjau dosen; daftar 80 kata per bulan diekspor ke `terms_review.csv` untuk dicek cepat. |
| Isi artikel bocor ke halaman | Pemeriksaan otomatis (§9): tidak ada 12-gram isi yang ada di `data.js`. Hanya judul, tag, tanggal, URL, angka. |
| `file://` memblokir fetch / modul ES | Data sebagai `data.js`; skrip klasik (`<script src>`), bukan `type="module"`. |
| Proyektor memudarkan warna dan garis tipis | Palet kontras ≥6:1, garis data ≥2px, uji di ruang kelas. |
| Mahasiswa membaca korelasi sebagai sebab | Keterangan tetap di P4 dan tips penutup §6. |
| Font tidak termuat (path salah) | Fallback `system-ui, monospace`; uji kriteria "0 permintaan jaringan". |

**Ditolak, dan alasannya**
- **Arwes:** berbasis React dan butuh bundler; untuk satu halaman offline, hasilnya bundle besar demi bingkai yang bisa dibuat dengan 40 baris CSS `clip-path` + SVG.
- **three.js dan 3d-force-graph:** jaringan 3D di proyektor = label saling menutupi dan perlu rotasi untuk dibaca. Bola kata cukup dengan DOM `translate3d`. Ini menghemat ±700 KB.
- **tsParticles:** murni dekorasi dan memakan GPU yang dibutuhkan P1.
- **ECharts:** tumpang tindih dengan D3 (±1 MB). Satu pustaka grafik saja (D3) sudah cukup.
- **TagCloud.js sebagai dependensi:** dibuang demi modul sendiri (butuh ukuran per kata, morph, sorot); tetap dipakai sebagai rujukan pola.
- **Analisis sentimen:** belum ada leksikon finansial Bahasa Indonesia yang tervalidasi untuk data ini, sehingga warnanya akan tampak meyakinkan tetapi tidak berdasar.
- **Topic modeling (LDA/BERTopic):** tidak stabil di 1.900 artikel pendek dan terlalu berat untuk satu sesi Minggu-09; c-TF-IDF per bulan memberi cerita yang sama secara lebih transparan.
- **Cuplikan/kalimat isi artikel di tooltip:** melanggar batas hak cipta.
- **Suara/efek bunyi J.A.R.V.I.S.:** mengganggu kelas dan bukan bagian dari data.

---

## 9. Pembagian kerja (3 pekerja paralel)

### Kontrak bersama (dibekukan sebelum mulai)
- Struktur: `dashboard/index.html`, `dashboard/css/hud.css`, `dashboard/js/{bus.js, app.js, intro.js, timeline.js, ranks.js, bump.js, headlines.js, sphere.js, network.js}`, `dashboard/vendor/{d3.v7.min.js, force-graph.min.js, gsap.min.js, fonts/*.woff2}`, `dashboard/data/{*.json, data.js}`.
- **Bus state** (`bus.js`, milik P2): `HUD.state`, `HUD.set(patch)`, `HUD.on(key, fn)`; kunci: `month`, `mode`, `term`, `motion`.
- **Kontrak modul panel:** `window.Panels.X = create(el, data, HUD)` mengembalikan `{update(state), introIn(tl, at), resize(), destroy()}`. Panel tidak saling memanggil; semuanya lewat `HUD`.
- **Fixture:** Pekerja 1 menyerahkan `dashboard/data/sample.data.js` (2 bulan, skema lengkap, data asli kecil) paling lambat di jam pertama, agar Pekerja 2 dan 3 tidak menunggu.

### Pekerja 1: Praproses data
- Berkas: `src/dashboard/preprocess.py`, `src/dashboard/fetch_prices.py`, `src/dashboard/stopwords_domain.txt`, `src/dashboard/entities.txt`, `tests/dashboard/test_preprocess.py`. Keluaran: `dashboard/data/*.json`, `data.js`, `sample.data.js`, `terms_review.csv`.
- Penerimaan:
  - `python src/dashboard/preprocess.py` deterministik (dua kali jalan → `data.js` identik byte demi byte, kecuali `generated_at`).
  - Validasi skema (pytest): tiap bulan punya `freq` dan `khas` berisi 80 kata (atau semua kata yang lolos ambang bila bulan tipis); `cooc` ≤40 node, ≤90 sisi, graf terhubung.
  - Tidak ada kata dari stopword Sastrawi + domain di `terms`; `khas` Januari memuat `msci`.
  - **Uji hak cipta:** dari 50 artikel acak, tidak ada 12-gram berurutan dari `content` yang ditemukan di `data.js`.
  - `data.js` ≤ 1,5 MB; laporan konsol: n artikel, n isi kosong, n per bulan.

### Pekerja 2: Inti halaman, HUD, intro, dan panel 2D (P2, P4, P5, P6)
- Berkas: `index.html`, `css/hud.css`, `js/bus.js`, `js/app.js`, `js/intro.js`, `js/timeline.js`, `js/ranks.js`, `js/bump.js`, `js/headlines.js`, `vendor/` (unduh sekali, simpan dengan nomor versi di nama berkas + `vendor/VERSIONS.txt`).
- Penerimaan:
  - Dibuka lewat `file://` di Chrome dan Firefox dengan Wi-Fi mati: **0 galat konsol, 0 permintaan http(s)** (Playwright: `page.route('http*://**', abort)` lalu hitung permintaan = 0 dan `console.error` = 0).
  - Semua pintasan §6 berfungsi (uji Playwright: tekan → periksa `HUD.state`).
  - Intro ≤ 6,5 detik ±0,3, bisa dilewati dengan Enter; dengan emulasi `reducedMotion: 'reduce'`, intro ≤ 0,5 detik dan tidak ada animasi berulang.
  - Tidak ada teks <18px pada viewport 1920×1080 (skrip memeriksa `getComputedStyle` semua node teks).
  - Tangkapan layar 1920×1080 dan 1280×720 tanpa overflow/scroll halaman.

### Pekerja 3: Panel 3D dan jaringan (P1, P3)
- Berkas: `js/sphere.js`, `js/network.js` (+ `css` lokal di dalam modul, diawali `.p1-`/`.p3-`).
- Penerimaan:
  - P1 menampilkan tepat `min(80, terms[month][mode].length)` elemen kata; ganti bulan → jumlah tetap benar, tidak ada elemen yatim di DOM (cek setelah 11× tekan →).
  - P3 merender ≤40 node dan ≤90 sisi; klik node mengubah `HUD.state.term`.
  - **FPS:** dengan `?debug=1` (penghitung rAF di pojok), median ≥55 fps selama 10 detik dengan bola berputar dan jaringan diam, di 1920×1080 pada perangkat ASUMSI §5. Tidak ada *long task* >50ms saat transisi bulan (Performance panel).
  - Loop rAF berhenti saat `document.hidden`; dengan reduced-motion bola tidak berputar otomatis.
  - Kata di bola bisa difokus dengan Tab, dan Enter memilihnya.

### Integrasi (koordinator)
Gabungkan, jalankan ulang semua uji di atas pada data penuh, lalu lakukan uji di ruang kelas: baca P2 dan P5 dari baris paling belakang, dan coba alur mengajar §6 dari awal sampai akhir dalam ≤25 menit.
