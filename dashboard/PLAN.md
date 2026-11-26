# PLAN FINAL: Dashboard J.A.R.V.I.S. // IHSG 2026 (Minggu-09)

Hasil sintesis: DESIGN_OPUS.md (dasar, tetap berlaku) + DESIGN_SOL.md (kritik) + permintaan pengguna (kesan film Iron Man yang kuat, aset Blender).
**Bila PLAN.md bertentangan dengan DESIGN_OPUS.md, PLAN.md yang menang.** Bagian Opus yang tidak disebut di sini tetap berlaku (palet, tipografi, kontrak bus, pintasan keyboard, pipeline pembersihan).

## Keputusan (REVISI atas Opus)
1. **Data masukan:** `data/news/cnbc_{A,B,C}.csv` + `data/news/cnbc_ref_dosen.csv` (556 artikel dosen, 28 Jan–2 Apr, kolom sama, tanggal ISO). Dedup per `url`. Jumlah artikel dan cerita per bulan TIDAK boleh ditulis keras; semuanya berasal dari audit pipeline. Pengumpulan shard A dan B mungkin masih berjalan: jalankan ulang pipeline sebelum integrasi.
2. **Nama skor:** BUKAN c-TF-IDF. Namanya "skor kekhasan berbasis cakupan artikel" (`df_share × log(M / support)`), dengan `support` = jumlah bulan yang `df_share >= 0,15` dan `M` = jumlah bulan di korpus. Istilah dengan `months_present >= 10` dijaga di bawah istilah yang lebih khas; skor dihitung untuk semua kata yang lolos ambang df minimum sebelum dipotong menjadi 80 hasil. Rumus dan ambang ditampilkan di bantuan dari `IHSG_DATA.meta.khas`. Tombol M tetap FREKUENSI vs KHAS.
3. **FREKUENSI vs stopword:** mode FREKUENSI memakai stopword umum (Sastrawi) + pembersih boilerplate saja, TANPA stopword domain, supaya pelajaran "frekuensi mentah itu membosankan" benar-benar terlihat. Stopword domain dan derau dipakai untuk mode KHAS, jaringan, dan `ALL`.
4. **Bulan tipis (n < 50):** tampilkan n dan penanda `DATA TIPIS`; untuk n < 30 mode KHAS dinonaktifkan dan diberi keterangan, jangan klaim "kata khas bulan ini". Interval ketidakpastian tidak diperlukan, cukup peringatan jelas.
5. **Pemangkasan jaringan (urutan baru):** pilih kandidat node -> potong ke <=40 node berdasarkan df -> bangun spanning tree pada graf kandidat yang terhubung -> tambahkan sisi ber-NPMI tertinggi sampai <=90 sisi -> uji graf terhubung (komponen terbesar >= 90% node; sisanya dibuang). Tes pytest untuk kasus graf terputus.
6. **Posisi node antarbulan:** teruskan `x/y` lama sebagai titik awal, bebaskan `fx/fy` kecuali saat diseret.
7. **Tata letak fokus (revisi §2 Opus):** selalu tampak: P1 (hero), P2 (peringkat), P4 (garis waktu + harga). P3 (jaringan), P5 (judul), P6 (bump) berada di area detail BERTAB (satu tampil pada satu waktu; tombol 1-6 memperbesar). Di 1280x720 hero, P2, dan P4 mendapat ruang minimum yang diuji dengan tangkapan layar.
8. **Peran 3D (revisi penolakan three.js):** three.js dipakai HANYA untuk **inti hologram nonteks** di balik awan kata P1 (cincin/sektor yang bereaksi pada bulan aktif). Kata, angka, label, kontrol tetap DOM/SVG. Jaringan kata tetap 2D. Bola kata tetap DOM `translate3d` (sesuai Opus) dengan lapisan hologram three.js di belakangnya. Inti hologram wajib lolos anggaran frame (median >= 55 fps, tidak ada long task > 50 ms); bila gagal atau WebGL tidak ada, tampilkan gambar diam dari Blender.
9. **Rasa Iron Man (revisi §4-5 Opus):** tambahkan (a) intro Blender 3-4 detik + ritual "assembly" GSAP berlapis, (b) perubahan energi saat bulan/mode berganti (denyut cincin, sapuan cahaya sekali), (c) hologram pusat yang berfungsi data. Batas keras Opus tetap: tidak ada glow pada kata yang bergerak, tidak ada teks dekoratif palsu, satu elemen dekoratif bergerak per panel setelah intro, tombol lewati, dan `prefers-reduced-motion`.
10. **Hak cipta:** halaman hanya memuat judul, tag, tanggal, URL, frekuensi/skor. Uji 12-gram dari isi artikel terhadap `data.js` wajib lulus.
11. **Harga ^JKSE:** unduh dengan yfinance, cocokkan 27-29 Jan dengan judul berita sebelum anotasi dipakai; jika gagal, P4 tampil tanpa harga dengan keterangan. Level 8.300/4.900-5.100 masih ASUMSI sampai diverifikasi.

## Aset Blender (dikerjakan koordinator lewat MCP; worker tidak menyentuh Blender)
Kontrak lokasi (worker memakai pengganti sementara sampai aset tiba):
- `dashboard/assets/intro.webm` (+ `intro.mp4` bila WebM tidak tersedia) 3-4 detik, 1920x1080, tanpa audio, tanpa angka/kata yang bisa berubah; `intro_poster.png`.
- `dashboard/assets/core.glb` (<= 3 MB): inti hologram 2-3 cincin + sektor, satu material emissive, tanpa tekstur besar; bernama node `ring_a`, `ring_b`, `ring_c`, `sectors` agar dapat dianimasikan.
- `dashboard/assets/hud_tex.png` / `.webp`: tekstur radial/grid beropasitas rendah, hanya dipakai di P1/intro.
- `dashboard/assets/core_still.png`: gambar diam untuk fallback.
Total `dashboard/assets` <= 30 MB.

## Pembagian kerja (3 pekerja Codex paralel + koordinator)
Kontrak bus/modul panel dan struktur berkas: lihat DESIGN_OPUS.md §9 (ditambah `js/core3d.js`, `js/intro.js` milik Pekerja 3).
- **Pekerja 1 (data):** `src/dashboard/*`, `tests/dashboard/*`, keluaran `dashboard/data/*` + `data.js` + `sample.data.js` (dalam 1 jam pertama) + `audit.md` (jumlah per bulan, per sumber, isi kosong, kata KHAS per bulan untuk ditinjau manusia). Penerimaan: lihat Opus §9 Pekerja 1 + keputusan 2-6 dan 10-11 di atas.
- **Pekerja 2 (UI dan grafik 2D):** `index.html`, `css/`, `js/{bus,app,timeline,ranks,bump,headlines,network}.js`, `vendor/` (d3, force-graph, gsap, three; versi dipatok, >= 2 minggu, simpan `vendor/VERSIONS.txt`), font lokal. Penerimaan: Opus §9 Pekerja 2 + tata letak fokus (keputusan 7) + P3 jaringan.
- **Pekerja 3 (sinematik):** `js/{sphere,core3d,intro}.js`, pemutar intro, fallback, `?debug=1` penghitung FPS. Bekerja di atas `sample.data.js` dan aset pengganti sampai aset Blender tiba. Penerimaan: keputusan 8-9 + anggaran frame + reduced motion + fallback tanpa WebGL.
- **Koordinator (saya):** aset Blender, integrasi, jalankan ulang pipeline pada data final, uji lintas-panel, tinjauan independen akhir oleh sol.

## Gerbang integrasi (semua wajib)
Buka lewat `file://` dengan jaringan mati: 0 galat konsol, 0 permintaan http(s). Pintasan §6 Opus berfungsi. Intro <= 6,5 detik dan bisa dilewati. Tidak ada teks < 18 px di 1920x1080; tangkapan layar 1920x1080 dan 1280x720 tanpa overflow. Median >= 55 fps (`?debug=1`). Uji 12-gram lulus. Pipeline deterministik. Anotasi peristiwa merujuk judul nyata. Kelayakan akhir dinilai ulang oleh sol pada hasil nyata (bukan pada ringkasan).

## Belum diverifikasi (jangan ditulis sebagai fakta)
Level IHSG; ketersediaan ^JKSE; jarak baca di kelas; FPS di laptop kelas; ukuran WebM yang diputar offline di Chrome/Firefox.
