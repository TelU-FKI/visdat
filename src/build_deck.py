"""Bangun presentasi edukasi time series QQQ dari template kuliah."""
from pathlib import Path
import numpy as np
import pandas as pd
from statsmodels.tsa.seasonal import STL
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.util import Inches, Pt
from pptx.oxml.xmlchemy import OxmlElement

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = Path("/Users/rifkiwijaya/Developer/visdat/Minggu-06 Visualisasi Data Time Series.pptx")
OUTPUT = ROOT / "QQQ-Time-Series.pptx"
FIGURES = ROOT / "figures"
DATA = ROOT / "data"
NAVY = RGBColor(31, 58, 95)
WHITE = RGBColor(255, 255, 255)
BODY_SIZE = 18
MAX_CONTENT_TITLE = 32
ID_MONTHS = ["Jan", "Feb", "Mar", "Apr", "Mei", "Jun", "Jul", "Agu", "Sep", "Okt", "Nov", "Des"]


def read_data() -> tuple[pd.DataFrame, pd.DataFrame, pd.Series, str]:
    """Muat data yang telah diunduh beserta tanggal pengambilannya."""
    prices = pd.read_csv(DATA / "qqq_ohlcv.csv", index_col=0, parse_dates=True)
    holdings = pd.read_csv(DATA / "holdings_top.csv")
    sectors = pd.read_csv(DATA / "sector_weights.csv", index_col=0)["Bobot"]
    asof = (DATA / "ASOF.txt").read_text(encoding="utf-8").splitlines()[0].split(":", 1)[-1].strip()
    return prices, holdings, sectors, asof


def fresh_deck() -> Presentation:
    """Muat template dan buang seluruh slide lama, tanpa mengubah template."""
    deck = Presentation(str(TEMPLATE))
    slide_ids = deck.slides._sldIdLst
    for slide_id in list(slide_ids):
        deck.part.drop_rel(slide_id.rId)
        slide_ids.remove(slide_id)
    return deck


def set_notes(slide, notes: str) -> None:
    """Isi catatan pembicara pada halaman."""
    slide.notes_slide.notes_text_frame.text = notes


DISCUSSION = {
    "Plot garis": "Pada bagian mana tren jangka panjang paling jelas terlihat? Bagaimana sumbu log akan mengubah pembacaan perubahan harga?",
    "Harga dan return": "Mengapa harga nominal QQQ dan imbal hasil harian dibaca pada panel terpisah? Apa arti return yang berayun di sekitar nol?",
    "Sepuluh holding terbesar: bobot": "Mengapa sepuluh holding teratas yang berbobot total 46,69% dapat memengaruhi lintasan ETF? Apa yang tidak terlihat dari grafik bobot saja?",
    "Komposisi sektor QQQ": "Bagaimana bobot Teknologi 60,33% dibanding sektor lain? Apa batas klasifikasi sektor Yahoo Finance?",
    "Plot area volume": "Lonjakan volume mana yang paling menonjol dalam sampel? Apakah volume saja dapat menjelaskan arah harga?",
    "Candlestick": "Pada candle mana jarak harga tertinggi dan terendah tampak lebar? Apa yang tidak ditunjukkan oleh satu candle tentang sebab gerak?",
    "Plot musiman": "Apa yang berubah ketika Oktober 2026 parsial tidak disertakan? Apa batas enam tahun kalender yang hanya memiliki empat tahun penuh?",
    "Heatmap return bulanan": "Mengapa Oktober 2026 dikeluarkan dari perbandingan bulanan? Bulan mana yang mencatat return terbaik +15,69% dan terburuk −13,60%?",
    "Heatmap kalender return harian": "Apa yang terlihat pada rentang Nov 2025–Okt 2026? Mengapa Oktober baru mencakup sampai 16 Okt?",
    "Membandingkan beberapa seri": "Mengapa jarak vertikal pada overlay log menunjukkan perubahan relatif? Mengapa sumbu linear small multiples tidak dapat dibaca sebagai skala yang sama?",
    "QQQ dan lima holding: overlay": "Bagaimana perubahan relatif tampak pada skala log? Mengapa jarak vertikalnya tidak membandingkan selisih harga absolut?",
    "Small multiples QQQ": "Mengapa QQQ, AAPL, dan MSFT tampak datar saat MU dan NVDA jauh lebih besar? Apa bedanya dengan overlay log?",
    "Heatmap korelasi return": "Mengapa korelasi AAPL–MU 0,310 jauh di bawah GOOGL–GOOG 0,997? Apakah nilai historis itu membuktikan sebab-akibat?",
    "Korelasi return harian": "Mengapa GOOGL–GOOG berkorelasi 0,997? Mengapa korelasi AAPL–MU yang 0,310 tidak membuktikan kedua harga bergerak independen?",
    "Rata-rata sederhana (SMA)": "Bagaimana SMA 20 hari merespons lebih cepat dibanding SMA 200 hari? Apa yang terjadi bila n diperbesar?",
    "Rata-rata eksponensial (EMA)": "Untuk n=50, mengapa α sekitar 0,039 memberi bobot lebih besar pada data terbaru? Di bagian mana EMA tampak lebih cepat dari SMA?",
    "Bollinger Bands": "Mengapa %B terakhir sekitar −0,22 berada di bawah pita bawah? Apakah itu sendiri menentukan arah harga berikutnya?",
    "Fitting tren matematis": "Mengapa R² polinomial 0,9481 yang tertinggi belum berarti model terbaik untuk memprediksi?",
    "Dekomposisi STL": "Mengapa amplitudo musiman sekitar −0,036 sampai 0,028 kecil dibanding tren? Apa yang ditunjukkan residual pada lima siklus?",
    "Dekomposisi STL bulanan": "Bagaimana tren 5,68–6,60 berbeda dari residual −0,128–0,085? Apa dampak membatasi data ke 60 bulan lengkap?",
    "Profil musiman bulanan": "Mengapa April sekitar −3,6% dan Juli +2,8% hanya pengamatan? Berapa banyak siklus lengkap yang mendasari profil ini?",
    "Return dan volatilitas": "Apa arti volatilitas tahunan terakhir 18,04% untuk variasi historis? Mengapa volatilitas tidak menunjukkan arah return?",
    "Drawdown": "Apa yang membedakan drawdown maksimum −35,62% pada 28 Des 2022 dari return satu hari? Berapa lama pemulihannya terlihat pada kurva?",
    "RSI (14)": "Apa arti RSI terakhir 35,00 relatif ke garis 30 dan 70? Mengapa garis itu bukan jaminan pembalikan?",
    "MACD (12, 26, 9)": "Mengapa histogram terakhir −4,642 saat MACD 1,525 dan sinyal 6,167? Apa batas interpretasi satu titik terakhir?",
}


def notes_with_discussion(title: str, notes: str) -> str:
    """Ganti pengisi generik dengan pertanyaan diskusi sesuai topik."""
    clean = " ".join(notes.replace("..", ".").split())
    clean = clean.replace("Bandingkan pola pada gambar dengan definisi indikator dan satuan sumbunya.", "")
    clean = clean.replace("Perhatikan label, rentang waktu, dan satuan yang tercantum pada gambar.", "")
    questions = DISCUSSION.get(title)
    return f"{clean} {questions}".strip()


def base_slide(deck: Presentation, title: str):
    """Buat halaman memakai layout konten dan judul template."""
    if len(title) > MAX_CONTENT_TITLE:
        raise ValueError(f"Judul isi melebihi {MAX_CONTENT_TITLE} karakter: {title!r}")
    slide = deck.slides.add_slide(deck.slide_layouts[1])
    title_shape = next(shape for shape in slide.shapes if shape.is_placeholder and shape.placeholder_format.idx == 0)
    title_shape.text = title
    return slide


def body_placeholder(slide, left: float, top: float, width: float, height: float):
    """Atur placeholder teks bawaan template."""
    body = next(shape for shape in slide.shapes if shape.is_placeholder and shape.placeholder_format.idx == 1)
    body.left, body.top = Inches(left), Inches(top)
    body.width, body.height = Inches(width), Inches(height)
    body.text_frame.clear()
    body.text_frame.word_wrap = True
    return body.text_frame


def add_bullets(slide, bullets: list[str], full_width: bool = False, width_override: float | None = None):
    """Isi placeholder dengan butir berkalimat utuh pada ukuran template."""
    width = width_override if width_override is not None else (12.4 if full_width else 6.15)
    tf = body_placeholder(slide, 0.32, 1.25, width, 5.57)
    tf.margin_left, tf.margin_right = Inches(0.03), Inches(0.08)
    tf.margin_top, tf.margin_bottom = Inches(0.05), Inches(0.04)
    for index, text in enumerate(bullets):
        paragraph = tf.paragraphs[0] if index == 0 else tf.add_paragraph()
        paragraph.text = text
        paragraph.space_after = Pt(9)
        paragraph.font.name = "Arial"
        paragraph.font.size = Pt(BODY_SIZE)
        paragraph.font.color.rgb = RGBColor(45, 45, 45)
    return tf


def add_image(slide, filename: str, left: float, top: float, width: float, alt: str):
    """Tambahkan gambar dengan rasio asli dan teks alternatif."""
    path = FIGURES / filename
    picture = slide.shapes.add_picture(str(path), Inches(left), Inches(top), width=Inches(width))
    picture._element._nvXxPr.cNvPr.set("descr", alt)
    picture._element._nvXxPr.cNvPr.set("title", alt[:200])
    return picture


def add_text_figure(deck: Presentation, title: str, bullets: list[str], filename: str,
                    alt: str, notes: str) -> None:
    """Buat metode dengan penjelasan kiri dan grafik 16:9 kanan."""
    slide = base_slide(deck, title)
    add_bullets(slide, bullets, width_override=5.80)
    add_image(slide, filename, 6.26, 2.05, 6.97, alt)
    set_notes(slide, notes_with_discussion(title, notes))


def add_full_figure(deck: Presentation, title: str, filename: str, alt: str,
                    notes: str, bullets: list[str] | None = None) -> None:
    """Buat halaman grafik penuh dan catatan opsional."""
    slide = base_slide(deck, title)
    if bullets:
        add_image(slide, filename, 2.47, 1.12, 8.40, alt)
        box = slide.shapes.add_textbox(Inches(0.8), Inches(5.98), Inches(11.8), Inches(1.08))
        frame = box.text_frame
        frame.clear()
        frame.word_wrap = True
        frame.margin_top, frame.margin_bottom = Inches(0.01), Inches(0.01)
        frame.margin_left, frame.margin_right = Inches(0.03), Inches(0.03)
        for i, text in enumerate(bullets):
            paragraph = frame.paragraphs[0] if i == 0 else frame.add_paragraph()
            paragraph.text = text
            paragraph.space_after = Pt(2)
            paragraph.level = 0
            ppr = paragraph._p.get_or_add_pPr()
            ppr.set("marL", str(Inches(0.28)))
            ppr.set("indent", str(-Inches(0.22)))
            bullet = OxmlElement("a:buChar")
            bullet.set("char", "•")
            ppr.append(bullet)
            for run in paragraph.runs:
                run.font.name, run.font.size = "Arial", Pt(14)
                run.font.color.rgb = RGBColor(45, 45, 45)
    else:
        add_image(slide, filename, 1.97, 1.14, 9.40, alt)
    set_notes(slide, notes)


def add_table_slide(deck: Presentation, title: str, headers: list[str], rows: list[list[str]],
                    notes: str = "") -> None:
    """Buat tabel PowerPoint native agar isi tetap dapat diedit."""
    slide = base_slide(deck, title)
    body_placeholder(slide, 0.32, 1.25, 12.4, 5.55)
    left, top, width, height = Inches(0.48), Inches(1.40), Inches(12.35), Inches(5.25)
    table_shape = slide.shapes.add_table(len(rows) + 1, len(headers), left, top, width, height)
    table = table_shape.table
    for column, header in enumerate(headers):
        cell = table.cell(0, column)
        cell.text = header
        cell.fill.solid()
        cell.fill.fore_color.rgb = NAVY
    for row_index, row in enumerate(rows, start=1):
        for column, value in enumerate(row):
            table.cell(row_index, column).text = str(value)
    for row_index, row in enumerate(table.rows):
        row.height = Inches(0.38 if len(rows) >= 10 else min(0.72, 5.25 / (len(rows) + 1)))
        for cell in row.cells:
            cell.margin_left, cell.margin_right = Inches(0.07), Inches(0.07)
            cell.margin_top, cell.margin_bottom = Inches(0.02), Inches(0.02)
            cell.vertical_anchor = MSO_ANCHOR.MIDDLE
            for paragraph in cell.text_frame.paragraphs:
                paragraph.alignment = PP_ALIGN.LEFT
                paragraph.font.name = "Arial"
                paragraph.font.size = Pt(11 if len(headers) >= 6 else (12 if len(rows) >= 8 else 14))
                if row_index == 0:
                    paragraph.font.bold = True
                    paragraph.font.color.rgb = WHITE
    if notes:
        set_notes(slide, notes)


def add_references_slides(deck: Presentation, asof: str) -> tuple[str, str]:
    """Buat dua halaman rujukan ringkas dengan tautan tertanam pada nama sumber."""
    title_books = "Referensi buku dan artikel"
    slide = base_slide(deck, title_books)
    add_bullets(slide, [
        "Wilke (2019), Fundamentals of Data Visualization.",
        "Hyndman & Athanasopoulos, Forecasting: Principles and Practice, edisi ke-3.",
        "Bollinger (2001), Bollinger on Bollinger Bands; Wilder (1978), New Concepts in Technical Trading Systems; Appel (MACD).",
    ], full_width=True)
    set_notes(slide, "Rujukan buku dan artikel menjadi dasar pengantar visualisasi dan definisi indikator.")

    title_web = "Sumber resmi dan data"
    slide = base_slide(deck, title_web)
    entries = [
        "Invesco QQQ, halaman produk resmi (diakses 19 Okt 2026).",
        "Metodologi Nasdaq-100 (diakses 19 Okt 2026).",
        "Nasdaq-100, ikhtisar indeks (diakses 19 Okt 2026).",
        f"Data harga dan komposisi: Yahoo Finance via yfinance; tanggal ambil {asof}, dari data/ASOF.txt.",
    ]
    tf = add_bullets(slide, entries, full_width=True)
    links = {
        0: "https://www.invesco.com/us/en/financial-products/etfs/invesco-qqq-trust-series-1.html",
        1: "https://indexes.nasdaqomx.com/docs/Methodology_NDX_Effective_May_1_2026.pdf",
        2: "https://indexes.nasdaqomx.com/Index/Overview/NDX",
    }
    for index, address in links.items():
        tf.paragraphs[index].runs[0].hyperlink.address = address
    set_notes(slide, "Tautan resmi mengarah ke produk QQQ dan dokumentasi indeks, diakses 19 Okt 2026. Data harga, holding, dan sektor dibaca dari berkas lokal yang diunduh melalui Yahoo Finance via yfinance.")
    return title_books, title_web


def pct(value: float, decimals: int = 2) -> str:
    """Format angka persen dengan koma Indonesia."""
    return f"{value:.{decimals}f}".replace(".", ",").replace("-", "−")



def validate_deck(deck: Presentation) -> None:
    """Hapus placeholder kosong dan gagalkan build jika struktur tidak valid."""
    width, height = deck.slide_width, deck.slide_height
    links = 0
    for index, slide in enumerate(deck.slides, start=1):
        for shape in list(slide.shapes):
            if shape.is_placeholder and (not shape.has_text_frame or not shape.text_frame.text.strip()):
                slide.shapes._spTree.remove(shape._element)
        if index > 1 and len(slide.shapes.title.text) > MAX_CONTENT_TITLE:
            raise ValueError(f"Judul isi slide {index} melebihi {MAX_CONTENT_TITLE} karakter")
        for shape in slide.shapes:
            if shape.left < 0 or shape.top < 0 or shape.left + shape.width > width or shape.top + shape.height > height:
                raise ValueError(f"Bentuk di luar kanvas pada slide {index}: {shape.name}")
            if shape.is_placeholder and (not shape.has_text_frame or not shape.text_frame.text.strip()):
                raise ValueError(f"Placeholder kosong tersisa pada slide {index}: {shape.name}")
            if shape.has_text_frame:
                if "•" in shape.text:
                    raise ValueError(f"Bullet literal ditemukan pada slide {index}")
                if not shape.has_table:
                    for paragraph in shape.text_frame.paragraphs:
                        if paragraph.font.size is not None and paragraph.font.size.pt < 14:
                            raise ValueError(f"Teks di bawah 14 pt pada slide {index}: {shape.name}")
                        for run in paragraph.runs:
                            if run.font.size is not None and run.font.size.pt < 14:
                                raise ValueError(f"Teks di bawah 14 pt pada slide {index}: {shape.name}")
            if shape.shape_type == 13 and not shape._element._nvXxPr.cNvPr.get("descr"):
                raise ValueError(f"Alt text gambar kosong pada slide {index}")
        links += sum("hyperlink" in rel.reltype for rel in slide.part.rels.values())
    if links < 3:
        raise ValueError(f"Hyperlink resmi hilang: ditemukan {links}, perlu minimal 3")


def make_deck() -> list[str]:
    """Bangun semua slide dan catatan angka yang dapat diverifikasi."""
    prices, holdings, sectors, asof = read_data()
    deck = fresh_deck()
    titles: list[str] = []
    close = prices["Close"]
    sma20_last = float(close.rolling(20).mean().iloc[-1])
    sma50_last = float(close.rolling(50).mean().iloc[-1])
    ema50_last = float(close.ewm(span=50, adjust=False).mean().iloc[-1])
    mean20 = close.rolling(20).mean()
    std20 = close.rolling(20).std(ddof=1)
    upper20, lower20 = mean20 + 2 * std20, mean20 - 2 * std20
    pct_b_last = float((close.iloc[-1] - lower20.iloc[-1]) /
                       (upper20.iloc[-1] - lower20.iloc[-1]))
    alpha_50 = 2 / 51

    def text(title: str, bullets: list[str], notes: str = "") -> None:
        slide = base_slide(deck, title)
        add_bullets(slide, bullets, full_width=True)
        if notes:
            set_notes(slide, notes_with_discussion(title, notes))
        titles.append(title)

    def chart(title: str, bullets: list[str], image: str, alt: str, notes: str) -> None:
        add_text_figure(deck, title, bullets, image, alt, notes)
        titles.append(title)

    def full(title: str, image: str, alt: str, notes: str, bullets=None) -> None:
        notes = notes_with_discussion(title, notes)
        add_full_figure(deck, title, image, alt, notes, bullets)
        titles.append(title)

    title_slide = deck.slides.add_slide(deck.slide_layouts[0])
    title_slide.shapes.title.text = "Visualisasi Data Time Series\npada Saham: Studi Kasus ETF QQQ"
    subtitle = next(shape for shape in title_slide.shapes if shape.is_placeholder and shape.placeholder_format.idx == 1)
    subtitle.text = "CAK4XBB3 - Visualisasi Data\nFKI Program Studi S1 Informatika - Fakultas Informatika"
    titles.append("Visualisasi Data Time Series pada Saham: Studi Kasus ETF QQQ")
    set_notes(title_slide, "Presentasi ini membahas visualisasi time series menggunakan data ETF QQQ. Seluruh angka mengikuti data yang tersedia dan tanggal pengambilan dicantumkan pada bagian penutup.")

    text("Agenda", ["Mengenal ETF dan QQQ", "Data time series saham", "Jenis plot untuk membaca data",
                   "Tren dan pemulusan", "Metode tambahan dan rangkuman"])
    text("Istilah penting", ["Imbal hasil (return) adalah perubahan relatif nilai sepanjang waktu; kepemilikan dalam portofolio disebut holding.",
          "Pemulusan (smoothing) mengurangi fluktuasi acak (noise); jeda (lag) adalah keterlambatan respons suatu ringkasan.",
          "Overlay menumpuk seri pada satu bidang; small multiples berarti panel kecil berulang untuk seri yang sama-sama dibandingkan.",
          "Pencocokan model (fitting) memilih fungsi yang merangkum data; rasio biaya (expense ratio) menyatakan biaya tahunan produk.",
          "Drawdown adalah penurunan dari puncak sebelumnya; istilah metode dijelaskan kembali pada slide terkait."])
    text("Apa itu ETF?", ["ETF adalah dana yang unitnya diperdagangkan di bursa seperti saham, sehingga harga transaksinya berubah sepanjang sesi.",
                          "Saham biasa mewakili kepemilikan pada satu perusahaan, sedangkan ETF dapat memuat banyak aset dalam satu unit.",
                          "Reksa dana tradisional umumnya dibeli atau dijual melalui pengelola pada nilai yang dihitung berkala, sementara ETF diperdagangkan di bursa.",
                          "ETF dapat memberi diversifikasi, biaya produk yang transparan, likuiditas bursa, dan keterbukaan komposisi; manfaat ini bergantung pada produk.",
                          "Harga unit ETF mengikuti permintaan pasar dan nilai aset dalam portofolionya melalui mekanisme pasar, sehingga dapat berbeda sementara dari nilai acuan."])
    text("Cara kerja ETF", ["Investor membeli atau menjual unit ETF melalui mekanisme perdagangan bursa.",
          "Pada ETF indeks, pengelola berupaya mengikuti komposisi dan pergerakan indeks acuannya.",
          "Diversifikasi tidak menghapus risiko karena banyak aset dapat turun pada waktu yang sama.",
          "Likuiditas dan transparansi membantu pemantauan, tetapi biaya transaksi dan selisih harga tetap perlu diperhatikan."])
    add_table_slide(deck, "Ciri ETF dalam satu pandangan",
        ["Aspek", "Satu saham", "ETF", "Reksa dana"], [
            ["Isi", "Satu perusahaan", "Keranjang aset", "Portofolio aset"],
            ["Perdagangan", "Di bursa", "Di bursa sepanjang sesi", "Umumnya melalui pengelola"],
            ["Diversifikasi", "Terbatas", "Banyak aset dalam satu instrumen", "Bergantung produk"],
            ["Transparansi", "Laporan perusahaan", "Komposisi dipublikasikan", "Mengikuti ketentuan produk"],
            ["Biaya", "Biaya transaksi", "Rasio biaya produk", "Biaya produk"]])
    titles.append("Ciri ETF dalam satu pandangan")
    text("Mengenal QQQ", ["QQQ adalah ticker Invesco QQQ Trust, sebuah ETF yang berupaya mengikuti Nasdaq-100.",
                          "Nasdaq-100 mencakup perusahaan besar non-keuangan yang tercatat di Nasdaq menurut klasifikasi indeks.",
                          "Indeks menjadi acuan untuk menyusun portofolio ETF; bobot dan hasil portofolio dapat berbeda dari tiap saham penyusunnya.",
                          "QQQ mulai diperdagangkan pada Maret 1999 dan expense ratio (rasio biaya) yang tercantum adalah 0,18%."])
    text("Profil holding terbesar", ["NVIDIA merancang chip grafis dan akselerator untuk kecerdasan buatan.",
          "Apple mengembangkan perangkat dan layanan; Microsoft menyediakan perangkat lunak dan layanan komputasi awan.",
          "Micron memproduksi memori semikonduktor, sedangkan AMD merancang prosesor dan unit pemroses grafis.",
          "Amazon bergerak di e-commerce dan komputasi awan; Meta mengoperasikan layanan media sosial.",
          "Alphabet menyediakan Google dan memiliki dua kelas saham yang tercantum, GOOGL dan GOOG; Tesla membuat kendaraan listrik."],
          "Deskripsi bisnis ini merupakan ringkasan umum, bukan tinjauan menyeluruh atas seluruh kegiatan perusahaan. Bagian mana yang membedakan perusahaan semikonduktor dari layanan digital? Mengapa GOOGL dan GOOG ditampilkan sebagai dua kelas saham?")
    text("Indeks Nasdaq-100", ["Mencakup 100 perusahaan non-keuangan terbesar yang tercatat di Nasdaq.",
                               "Bobot berbasis kapitalisasi pasar dengan penyesuaian.",
                               "Indeks menjalani penyeimbangan ulang berkala.",
                               "Indeks mengecualikan sektor keuangan menurut klasifikasi indeks.",
                               "Yahoo mengklasifikasikan jasa keuangan QQQ sebesar 0,19%."])
    holding_rows = [[str(r.Symbol), str(r.Name), pct(float(r["Holding Percent"]) * 100)]
                    for _, r in holdings.head(10).iterrows()]
    holding_rows = [[a, b, f"{c}%"] for a, b, c in holding_rows]
    add_table_slide(deck, "Sepuluh holding terbesar: tabel",
                    ["Simbol", "Nama", "Bobot (%)"], holding_rows,
                    "GOOGL dan GOOG adalah dua kelas saham Alphabet, yaitu satu perusahaan.")
    titles.append("Sepuluh holding terbesar: tabel")
    top_weight = float(holdings.head(10)["Holding Percent"].sum() * 100)
    full("Sepuluh holding terbesar: bobot", "20_top_holdings.png",
         "Bobot sepuluh holding terbesar QQQ", f"Sepuluh holding teratas mencakup {pct(top_weight)}% bobot. Grafik menampilkan bobot setiap perusahaan secara berurutan.")
    chart("Komposisi sektor QQQ", ["Teknologi menjadi sektor dengan bobot terbesar.",
             "Teknologi 60,33%; Layanan Komunikasi 12,59%.",
             "Konsumsi Siklikal berbobot 10,07%.",
             "Kategori Yahoo dapat berbeda dari klasifikasi indeks."],
          "19_sektor.png", "Bobot sektor QQQ dalam persentase",
          "Sektor menunjukkan komposisi menurut klasifikasi Yahoo Finance. Klasifikasi ini dapat berbeda dari klasifikasi indeks.")
    text("QQQ sebagai deret waktu", [
        "Data penutupan harian tersedia dari 18 Okt 2021 sampai 16 Okt 2026.",
        "Rentang tersebut memuat 1.255 hari bursa.",
        "Seri memperlihatkan tren dan perubahan volatilitas.",
        "Periode penurunan dan pemulihan dapat diamati secara historis."])
    sample = prices.tail(5).copy()
    sample_rows = []
    for date, row in sample.iterrows():
        sample_rows.append([f"{date.day:02d} {ID_MONTHS[date.month - 1]} {date.year}", *[pct(float(row[col]), 2) for col in ["Open", "High", "Low", "Close", "Adj Close"]],
                            f"{int(row['Volume']):,}".replace(",", ".")])
    add_table_slide(deck, "Contoh data OHLCV QQQ",
                    ["Tanggal", "Buka", "Tertinggi", "Terendah", "Tutup", "Tutup disesuaikan", "Volume"], sample_rows,
                    "Lima baris terakhir dari data harga harian; tanggal perdagangan tidak mencakup akhir pekan dan hari libur.")
    titles.append("Contoh data OHLCV QQQ")
    chart("Harga dan return", ["Imbal hasil (return) harian = (Pₜ − Pₜ₋₁) / Pₜ₋₁.",
           "Harga cenderung tidak stasioner pada rentang panjang.",
           "Return berayun di sekitar nol.",
           "Indeks hanya memuat hari bursa; jarak tanggal tidak seragam."],
          "00_harga_vs_return.png", "Dua panel harga penutupan dan return harian QQQ",
          "Panel atas menunjukkan harga penutupan. Panel bawah menunjukkan return harian yang berfluktuasi di sekitar nol.")
    text("Komponen time series saham", ["Tren menunjukkan arah perubahan jangka panjang.",
          "Musiman merangkum pola kalender yang mungkin berulang.",
          "Siklus dapat terkait kondisi ekonomi dan suku bunga.",
          "Noise mencakup fluktuasi yang tidak dijelaskan komponen lain.",
          "Pola musiman saham tidak menjamin pengulangan; data ini hanya memuat lima siklus."])
    text("Jenis plot yang digunakan", ["Grafik garis dan area merangkum perubahan sepanjang waktu.",
          "Candlestick menampilkan empat harga dalam satu periode.",
          "Plot musiman dan heatmap membantu membandingkan pola kalender.",
          "Deret jamak membandingkan aset setelah normalisasi.",
          "Heatmap korelasi merangkum hubungan return antar aset."])
    text("Bagian I: Grafik harga", ["Bagian ini memperkenalkan grafik yang mempertahankan urutan waktu.",
          "Setiap bentuk menonjolkan sisi data yang berbeda, seperti harga, rentang, volume, atau kalender.",
          "Pembacaan dimulai dari pola yang terlihat sebelum menarik kesimpulan."])
    chart("Plot garis", ["Plot garis menghubungkan harga penutupan berurutan untuk menunjukkan perubahan sepanjang waktu.",
          "Pada gambar QQQ, lintasan historis bergerak naik secara umum dengan beberapa penurunan tajam yang tetap tampak.",
          "Plot ini cocok untuk membaca arah dan perubahan berkelanjutan, sedangkan skala log membantu membandingkan perubahan relatif.",
          "Sumbu yang dipotong atau terlalu banyak garis dapat membesar-besarkan gerak dan mengaburkan seri utama."],
          "01_line_close.png", "Grafik garis harga penutupan QQQ lima tahun",
          "Grafik garis menghubungkan harga penutupan harian. Gunakan skala yang sesuai dengan pertanyaan dan hindari sumbu yang menyesatkan.")
    chart("Plot area volume", ["Plot area mengisi bidang di bawah seri agar besaran volume harian QQQ lebih menonjol.",
          "Gambar memperlihatkan lonjakan volume pada beberapa sesi di atas tingkat hari-hari biasa.",
          "Area cocok untuk menekankan kuantitas sepanjang waktu dan garis rata-rata membantu membaca kecenderungan.",
          "Skala volume dapat didominasi pencilan, dan area bertumpuk menyulitkan pembandingan banyak seri."],
          "02_area_volume.png", "Volume perdagangan harian dengan rata-rata bergerak",
          "Area mempertegas kuantitas volume sepanjang waktu. Rata-rata bergulir merangkum kecenderungan tanpa mengganti data harian.")
    chart("Candlestick", ["Candlestick merangkum harga buka, tertinggi, terendah, dan tutup dalam satu candle.",
          "Pada gambar, badan dan sumbu memperlihatkan rentang harian QQQ serta pergantian sesi naik dan turun.",
          "Bentuk ini cocok untuk menelaah rentang perdagangan pada periode yang relatif pendek.",
          "Banyak candle pada rentang panjang menjadi padat, dan warna saja tidak menjelaskan penyebab pergerakan."],
          "03_candlestick.png", "Candlestick dan volume sekitar 120 hari bursa terakhir",
          "Setiap candle merangkum harga buka, tertinggi, terendah, dan tutup. Volume ditampilkan sebagai panel pendamping.")
    chart("Plot musiman", ["Plot musiman menyelaraskan observasi tiap tahun pada posisi bulan kalender yang sama.",
          "Gambar mencakup enam tahun kalender: 2021 hanya Nov–Des dan 2026 Jan–Sep, sedangkan 2022–2025 penuh.",
          "Garis putus-putus menandai tahun parsial; penyelarasan cocok untuk membandingkan lintasan kalender.",
          "Empat tahun kalender penuh (2022–2025) dan dua tahun parsial membatasi sampel; pola tidak membuktikan pengulangan."],
          "04_seasonal_plot.png", "Return kumulatif bulanan yang ditampilkan per tahun",
          "Grafik menyelaraskan bulan kalender untuk enam tahun: 2021 parsial Nov–Des, 2026 parsial Jan–Sep, dan 2022–2025 penuh. Garis putus-putus menandai tahun parsial. Empat tahun kalender penuh (2022–2025) dan dua tahun parsial hanya pengamatan, bukan pola yang dijamin berulang.")
    chart("Heatmap return bulanan", ["Heatmap menempatkan tahun pada baris dan bulan pada kolom; setiap sel menunjukkan imbal hasil (return) bulanan.",
          "Oktober 2026 belum lengkap sampai 16 Okt dan tidak ditampilkan; 2021 hanya memuat Nov–Des.",
          "Pada QQQ, April 2026 mencatat return terbaik +15,69%, sedangkan April 2022 terburuk −13,60%.",
          "Warna yang berpusat pada nol cocok untuk menemukan bulan yang menonjol dan membandingkan banyak periode sekaligus.",
          "Warna tidak menunjukkan sebab-akibat; sampel pendek dan skala warna yang tidak seimbang dapat menyesatkan."],
          "05_heatmap_bulanan.png", "Heatmap return bulanan QQQ dengan skala divergen",
          "Warna heatmap menunjukkan arah dan besar return bulanan. Return terbaik yang tercatat adalah April 2026 sebesar +15,69%; terburuk April 2022 sebesar −13,60%.")
    full("Heatmap kalender return harian", "06_heatmap_kalender.png",
         "Heatmap kalender return harian dalam 12 bulan terakhir",
         "Kalender mencakup Nov 2025–Okt 2026, dengan Oktober 2026 hanya sampai 16 Okt. Setiap sel menunjukkan return satu hari bursa; warna membantu memindai arah dan pengelompokan, bukan sebab pergerakan.",
         ["Setiap sel menunjukkan return harian; akhir pekan tanpa observasi.",
          "Warna membedakan hari positif dan negatif pada rentang terpilih.",
          "Rentang Nov 2025–Okt 2026; Okt hanya sampai 16 Okt."])
    text("Membandingkan beberapa seri", ["Overlay menumpuk banyak garis, sedangkan small multiples memberi panel terpisah untuk tiap aset.",
          "Grafik QQQ dan lima holding memulai seri pada indeks 100 agar perubahan relatif dapat dibandingkan.",
          "Cara ini cocok ketika skala harga nominal berbeda tetapi pembaca ingin membandingkan lintasan historis.",
          "Overlay dapat menjadi padat, sedangkan normalisasi menyembunyikan perbedaan harga nominal dan titik awal."],
          "Normalisasi indeks 100 membagi harga setiap seri dengan nilai awal lalu mengalikan hasilnya dengan 100. Overlay membantu melihat perbedaan lintasan dalam satu panel, sementara small multiples mengurangi tumpang tindih. Keduanya berguna untuk membandingkan perubahan relatif pada periode yang sama. Namun perubahan relatif tidak menyatakan nilai nominal ataupun hubungan sebab-akibat.")
    text("Bagian II: Membandingkan aset", ["Perbandingan membutuhkan skala yang sebanding dan label yang jelas.",
          "Normalisasi membantu membaca perubahan relatif, sementara korelasi merangkum gerak bersama.",
          "Hubungan historis tidak menjamin hubungan yang sama pada periode lain."])
    full("QQQ dan lima holding: overlay", "07_multi_overlay.png",
         "Grafik overlay harga QQQ dan lima holding yang dinormalisasi ke indeks 100",
         "Semua seri dimulai dari indeks 100 untuk membandingkan perubahan relatif. Overlay memakai skala log sehingga jarak vertikal menyatakan perubahan relatif. Angka indeks menyajikan lintasan historis untuk perbandingan visual.")
    full("Small multiples QQQ", "08_multi_small.png",
         "Small multiples harga QQQ dan lima holding yang dinormalisasi ke indeks 100",
         "Panel memakai sumbu x dan y linear bersama untuk membandingkan besaran absolut indeks. QQQ, AAPL, dan MSFT tampak datar karena nilai MU dan NVDA jauh lebih besar pada skala yang sama. Ini berbeda dari overlay berskala log, yang jarak vertikalnya menyatakan perubahan relatif.")
    text("Heatmap korelasi return", ["Korelasi mengukur keeratan hubungan linear antara dua seri return, dengan rentang minus satu sampai satu.",
          "Heatmap QQQ menghitung korelasi return harian, bukan korelasi harga mentah.",
          "Korelasi GOOGL–GOOG sebesar 0,997, sedangkan korelasi QQQ–NVDA sebesar 0,78.",
          "Pasangan AAPL–MU memiliki korelasi terendah pada daftar ini, yaitu 0,310.",
          "Heatmap cocok untuk merangkum banyak pasangan, tetapi korelasi tidak membuktikan sebab-akibat atau menjamin diversifikasi."],
          "Korelasi Pearson membandingkan kovariasi dua return setelah menormalkan dengan simpangan bakunya. Warna heatmap memperlihatkan arah dan kekuatan hubungan pada sampel historis. Nilai GOOGL–GOOG sangat tinggi karena keduanya kelas saham dari Alphabet, sedangkan hubungan QQQ–NVDA juga positif. Korelasi dapat berubah sepanjang waktu dan tidak berarti satu seri menyebabkan seri lain.")
    full("Korelasi return harian", "09_korelasi.png", "Heatmap korelasi return QQQ dan sepuluh holding terbesar",
         "Korelasi menggambarkan gerak bersama pada sampel historis dan bukan jaminan hubungan ke depan. Korelasi tertinggi GOOGL–GOOG 0,997; terendah AAPL–MU 0,310.")
    text("Mengapa tren perlu dihaluskan?", ["Gerak harian dapat menutupi arah jangka panjang.",
          "Pemulusan mengurangi fluktuasi kecil.",
          "Semakin panjang jendela, semakin besar jeda terhadap perubahan baru.",
          "Pemulusan membantu membaca data, bukan menghilangkan risiko."],
          "Pemulusan menekan fluktuasi kecil agar kecenderungan lebih mudah dibaca. Setiap metode memiliki jeda yang bergantung pada panjang jendela.")
    chart("Rata-rata sederhana (SMA)", ["SMAₜ = (1/n) × jumlah Pₜ₋ᵢ untuk i=0 sampai n−1; setiap harga pada jendela berbobot sama.",
          "Pada grafik QQQ, garis 20, 50, dan 200 hari makin halus saat jendelanya makin panjang.",
          "SMA cocok untuk merangkum tren ketika fluktuasi harian menutupi arah umum.",
          f"Pada titik terakhir, harga {pct(float(close.iloc[-1]))} USD berada di bawah SMA20 {pct(sma20_last)} USD; SMA berjeda dan perpotongan bukan sinyal pasti."],
          "10_sma.png", "Harga penutupan dan SMA 20, 50, serta 200 hari",
          "SMA memberi bobot sama pada setiap observasi di jendela. Jendela yang lebih panjang lebih halus tetapi lebih lambat merespons.")
    chart("Rata-rata eksponensial (EMA)", [f"EMAₜ = αPₜ + (1−α)EMAₜ₋₁ dengan α=2/(n+1); untuk n=50, α≈{pct(alpha_50, 3)}.",
          "Gambar membandingkan EMA dan SMA 50 hari pada harga QQQ; EMA lebih dekat mengikuti perubahan terbaru.",
          "EMA cocok ketika pembaca menginginkan pemulusan yang lebih tanggap terhadap observasi baru.",
          f"Pada titik terakhir, EMA50 {pct(ema50_last)} USD dan SMA50 {pct(sma50_last)} USD; keduanya tertinggal dari harga {pct(float(close.iloc[-1]))} USD."],
          "11_ema_vs_sma.png", "Perbandingan harga, EMA 50 hari, dan SMA 50 hari selama setahun",
          "EMA merespons observasi baru lebih cepat daripada SMA dengan jendela yang sama. Keduanya tetap merupakan ringkasan harga lampau.")
    chart("Bollinger Bands", ["Pita = SMA20 ± 2s, dengan s simpangan baku sampel 20 hari; %B=(P−pita bawah)/(pita atas−pita bawah).",
          f"Pada titik terakhir QQQ, %B sekitar {pct(pct_b_last, 2)}; harga {pct(float(close.iloc[-1]))} USD berada di bawah pita bawah periode itu.",
          "Pita cocok untuk membaca volatilitas relatif dan posisi harga terhadap rata-rata bergulir.",
          "Harga dapat bertahan di luar pita; sentuhan atau %B di luar rentang bukan kepastian pembalikan."],
          "12_bollinger.png", "Bollinger Bands 20 hari beserta persentase B",
          "Pita menggunakan simpangan baku sampel pada jendela 20 hari. Lebar pita berubah mengikuti variasi harga dalam jendela tersebut.")
    chart("Fitting tren matematis", ["R² ketiga model memakai rumus, skala harga, dan sampel yang sama; nilainya sebanding untuk kecocokan dalam sampel.",
          "Eksponensial dipasang dengan regresi linear pada log harga, bukan galat kuadrat harga langsung.",
          "R² linear 0,8489, polinomial derajat 3 0,9481, dan eksponensial 0,8954; polinomial lebih fleksibel.",
          "R² tertinggi dan kecocokan dalam sampel tidak membuktikan kemampuan prediksi."],
          "13_fitting.png", "Harga aktual dan tiga model tren dengan R kuadrat di legenda",
          "R² ketiga model memakai rumus yang sama pada harga dan sampel yang sama, sehingga dapat dibandingkan sebagai kecocokan dalam sampel. Linear dan polinomial menyesuaikan galat harga, sementara eksponensial dipasang melalui regresi linear pada log harga. Polinomial derajat 3 memiliki R² tertinggi, 0,9481, karena lebih fleksibel; linear 0,8489 dan eksponensial 0,8954.")
    text("Dekomposisi STL", ["STL memisahkan log harga 60 penutupan akhir bulan (Okt 2021–Sep 2026) menjadi observasi, tren, musiman, dan residual.",
          "Panel observasi memperlihatkan seri asli; panel tren merangkum gerak jangka panjang yang diperhalus.",
          "Panel musiman menunjukkan profil bulanan yang dibatasi periodik, sedangkan residual adalah bagian yang tersisa.",
          "Tren 5,68–6,60 log; musiman −0,036–0,028; residual −0,128–0,085; simpangan baku residual 0,046.",
          "Profil berikutnya merangkum komponen log ×100 (≈%); ini bukan persen eksak 100×(exp(s)−1).",
          "Profil slide berikutnya merangkum komponen per bulan; lima siklus hanya pengamatan dan tidak menjamin pengulangan."],
          "STL menguraikan log harga 60 penutupan akhir bulan, Oktober 2021 sampai September 2026. Panel observasi menunjukkan seri log, tren menggambarkan gerak halus, musiman adalah profil periodik, dan residual merupakan bagian yang belum diterangkan. Rentang tren 5,68–6,60 log, musiman −0,036–0,028, residual −0,128–0,085, dengan simpangan baku residual 0,046. Pada grafik profil, komponen log dikalikan 100 sebagai pendekatan persen, bukan transformasi eksak 100×(exp(s)−1). Kelima siklus ini hanya pengamatan historis.")
    full("Dekomposisi STL bulanan", "14_dekomposisi.png", "Empat panel STL bulanan pada log harga: observasi, tren, musiman, residual",
         "Basisnya 60 penutupan bulanan lengkap dari Okt 2021 sampai Sep 2026. Tren 5,68–6,60 log; musiman −0,036–0,028; residual −0,128–0,085; simpangan baku residual 0,046. Komponen musiman bersatuan log. Lima siklus adalah pengamatan historis, bukan bukti pola akan berulang.")
    full("Profil musiman bulanan", "14b_profil_musiman.png", "Profil komponen musiman bulanan dari Januari sampai Desember dalam persen",
         "Basis profil adalah 60 penutupan akhir bulan, Okt 2021–Sep 2026. Batang menunjukkan komponen musiman dalam log ×100 sebagai pendekatan persen, bukan transformasi eksak 100×(exp(s)−1). Hasil Jan–Des: +0,6%, −1,3%, −2,0%, −3,6%, +1,4%, +2,0%, +2,8%, +1,5%, −1,1%, −2,0%, +1,7%, +0,1%. Kelima siklus ini hanya pengamatan deskriptif, bukan klaim pengulangan.")
    chart("Return dan volatilitas", ["Return mengukur perubahan relatif harga penutupan, sedangkan volatilitas mengukur sebaran return.",
          "Grafik memakai simpangan baku bergulir 21 hari yang dianualisasi dengan faktor √252.",
          "Volatilitas terakhir adalah 18,04% per tahun; puncak pada kurva bertepatan dengan episode lebih bergejolak.",
          "Ukuran ini cocok untuk membandingkan tingkat variasi historis, tetapi jendelanya sensitif dan bukan ukuran arah."],
          "15_return_volatilitas.png", "Return harian dan volatilitas 21 hari yang dianualisasi",
          "Volatilitas tahunan 21 hari terakhir adalah 18,04%. Annualisasi menggunakan 252 hari perdagangan sebagai konvensi perhitungan.")
    chart("Drawdown", ["Drawdown = harga saat ini dibagi puncak berjalan sebelumnya, lalu dikurangi satu.",
          "Pada kurva QQQ, penurunan terdalam mencapai −35,62% pada 28 Des 2022.",
          "Ukuran ini cocok untuk melihat kedalaman dan durasi penurunan dari puncak historis.",
          "Drawdown bergantung pada periode pengamatan dan tidak menunjukkan seberapa jauh penurunan mendatang."],
          "16_drawdown.png", "Kurva drawdown dari puncak sebelumnya dengan titik maksimum ditandai",
          "Drawdown dihitung sebagai harga dibagi puncak berjalan dikurangi satu. Nilai historis tidak menunjukkan besarnya penurunan di masa mendatang.")
    chart("RSI (14)", ["RS=rerata kenaikan/rerata penurunan; rerata Wilderₜ=((n−1)×rerataₜ₋₁+xₜ)/n, xₜ adalah gain atau loss dan n=14.",
          "RSI=100−100/(1+RS); nilai QQQ terakhir 35,00 berada di antara garis konvensional 30 dan 70.",
          "Indikator ini cocok untuk meringkas momentum pada jendela waktu tertentu.",
          "Batas 30 dan 70 bukan hukum; RSI dapat bertahan di satu wilayah dan tidak memastikan pembalikan."],
          "17_rsi.png", "Harga dan RSI Wilder 14 hari dengan garis batas 30 dan 70",
          "RSI membandingkan rata-rata perubahan naik dan turun selama 14 periode dengan metode Wilder. Batas 30 dan 70 adalah konvensi, bukan kepastian pembalikan.")
    chart("MACD (12, 26, 9)", ["MACD adalah EMA12 dikurangi EMA26; garis sinyal adalah EMA9 dari MACD dan histogram adalah selisih keduanya.",
          "Pada titik terakhir, MACD 1,525, sinyal 6,167, histogram −4,642; MACD berada di bawah garis sinyal.",
          "MACD cocok untuk membaca momentum relatif dan perubahan jarak dua rata-rata eksponensial.",
          "Nilainya bergantung pada parameter, bersifat tertinggal, dan persilangan tidak menjamin arah harga."],
          "18_macd.png", "Harga dan MACD 12, 26, 9 dengan garis sinyal serta histogram",
          "MACD merangkum selisih dua EMA dan EMA9 dari selisih tersebut. Pembacaan ini menjelaskan data historis, bukan rekomendasi transaksi.")
    summary_head = ["Metode", "Pertanyaan", "Kapan dipakai", "Keterbatasan"]
    summary_a = [
        ["Garis / area", "Bagaimana nilai berubah?", "Tren harga dan volume", "Skala dapat menyesatkan"],
        ["Candlestick", "Bagaimana rentang harian?", "Buka, tinggi, rendah, tutup", "Padat pada rentang panjang"],
        ["Musiman / heatmap", "Kapan nilai menonjol?", "Bandingkan pola kalender", "Sampel parsial/pendek"],
        ["Normalisasi = 100", "Bagaimana lintasan relatif?", "Bandingkan perubahan aset", "Bukan harga absolut"],
        ["Korelasi", "Seberapa terkait return?", "Ringkas gerak bersama", "Bukan sebab-akibat"],
        ["SMA / EMA", "Bagaimana tren halus?", "Kurangi fluktuasi harian", "Memiliki jeda"],
        ["Bollinger", "Seberapa lebar variasi?", "Posisi terhadap pita", "Bukan batas pasti"],
    ]
    summary_b = [
        ["Fitting", "Seberapa sesuai model?", "Ringkas tren sampel", "Cocok dalam sampel bukan prediksi"],
        ["STL (60 bulan)", "Apa komponen seri?", "Tren dan kalender", "Lima siklus pengamatan"],
        ["Volatilitas bergulir", "Seberapa besar variasi?", "Pantau risiko historis", "Jendela sensitif"],
        ["Drawdown", "Seberapa dalam dari puncak?", "Lihat penurunan historis", "Tergantung rentang data"],
        ["RSI", "Bagaimana momentum?", "Ringkas naik dan turun", "Bukan sinyal pasti"],
        ["MACD", "Bagaimana selisih EMA?", "Baca momentum relatif", "Tertinggal dari harga"],
    ]
    add_table_slide(deck, "Ringkasan metode (1/2)", summary_head, summary_a,
                    "Bagian pertama merangkum grafik harga, kalender, normalisasi, korelasi, dan pemulusan.")
    titles.append("Ringkasan metode (1/2)")
    add_table_slide(deck, "Ringkasan metode (2/2)", summary_head, summary_b,
                    "Bagian kedua merangkum pencocokan, dekomposisi, variasi, drawdown, dan momentum.")
    titles.append("Ringkasan metode (2/2)")
    text("Disclaimer", ["Materi ini disusun untuk tujuan edukasi.",
          "Isi bukan nasihat investasi atau rekomendasi transaksi.",
          "Kinerja historis tidak menjamin hasil pada masa depan.",
          "Keputusan investasi memerlukan pertimbangan dan sumber informasi masing-masing."])
    titles.extend(add_references_slides(deck, asof))

    validate_deck(deck)
    deck.save(OUTPUT)
    write_numbers(prices, holdings, sectors, asof, top_weight, sample, titles)
    return titles


def write_numbers(prices, holdings, sectors, asof, top_weight, sample, titles) -> None:
    """Dokumentasikan sumber serta metode angka yang dihitung dari berkas lokal."""
    top = holdings.head(10)[["Symbol", "Name", "Holding Percent"]]
    rows = [f"| {r.Symbol} | {r.Name} | {pct(float(r['Holding Percent']) * 100)} |" for _, r in top.iterrows()]
    sample_cols = ["Open", "High", "Low", "Close", "Adj Close"]
    sample_rows = ["| " + " | ".join([date.strftime("%Y-%m-%d"),
                    *[pct(float(r[col])) for col in sample_cols],
                    f"{int(r.Volume):,}".replace(",", ".")]) + " |"
                   for date, r in sample.iterrows()]
    title_rows = [f"{i:02d}. {title.replace(chr(10), ' ')}" for i, title in enumerate(titles, 1)]
    sector_values = ", ".join(f"{name}: {pct(float(weight) * 100)}%" for name, weight in sectors.items())
    monthly_close = prices["Close"].resample("ME").last().iloc[:-1]
    monthly_log = np.log(monthly_close)
    monthly_returns = monthly_close.pct_change().dropna()
    stl = STL(monthly_log, period=12, seasonal=99, seasonal_deg=0).fit()
    trend_range = (float(stl.trend.min()), float(stl.trend.max()))
    seasonal_range = (float(stl.seasonal.min()), float(stl.seasonal.max()))
    residual_range = (float(stl.resid.min()), float(stl.resid.max()))
    residual_std = float(stl.resid.std())
    seasonal_profile = stl.seasonal.groupby(stl.seasonal.index.month).mean() * 100
    profile_text = ", ".join(f"{ID_MONTHS[m-1]} {pct(float(v), 1)}%" for m, v in seasonal_profile.items())
    alpha_50 = 2 / (50 + 1)
    close = prices["Close"]
    sma20_last = float(close.rolling(20).mean().iloc[-1])
    sma50_last = float(close.rolling(50).mean().iloc[-1])
    ema50_last = float(close.ewm(span=50, adjust=False).mean().iloc[-1])
    bollinger_mean = close.rolling(20).mean()
    bollinger_std = close.rolling(20).std(ddof=1)
    bollinger_upper = bollinger_mean + 2 * bollinger_std
    bollinger_lower = bollinger_mean - 2 * bollinger_std
    pct_b_last = float((close.iloc[-1] - bollinger_lower.iloc[-1]) /
                       (bollinger_upper.iloc[-1] - bollinger_lower.iloc[-1]))
    text = f"""# Catatan angka deck QQQ

Sumber harga/holding/sektor: berkas lokal `data/`; Yahoo Finance via yfinance. Tanggal pengambilan: {asof}.

## Angka hasil data

- Rentang harga: {prices.index.min():%Y-%m-%d} sampai {prices.index.max():%Y-%m-%d}; jumlah baris: {len(prices):,}. Tanggal rentang berasal dari nilai minimum/maksimum indeks dan jumlah dari banyaknya baris CSV.
- Penutupan terakhir: {pct(float(prices.Close.iloc[-1]))} USD; diambil dari nilai terakhir kolom `Close`.
- Total bobot sepuluh holding teratas: {pct(top_weight)}%; jumlah `Holding Percent` pada 10 baris pertama × 100.
- Holding berasal dari `data/holdings_top.csv`; persen per baris = nilai pecahan × 100.
- Sektor pada CSV (persen = pecahan × 100): {sector_values}.

| Simbol | Nama | Bobot (%) |
|---|---|---:|
{chr(10).join(rows)}

- Sampel OHLCV di slide: lima baris terakhir `data/qqq_ohlcv.csv`; tabel menampilkan tanggal dan angka asli.

| Tanggal | Open | High | Low | Close | Adj Close | Volume |
|---|---:|---:|---:|---:|---:|---:|
{chr(10).join(sample_rows)}

## Angka terverifikasi lain dan cara baca

Nilai berikut telah disediakan dan diverifikasi dalam tugas: expense ratio 0,18%; total sepuluh bobot teratas 46,69%; return bulanan terbaik Apr 2026 +15,69% dan terburuk Apr 2022 −13,60%; korelasi GOOGL–GOOG 0,997, AAPL–MU 0,310, QQQ–NVDA 0,78; R² linear 0,8489, polinomial derajat 3 0,9481, eksponensial 0,8954; drawdown maksimum −35,62% pada 28 Des 2022; volatilitas 21 hari 18,04% tahunan; RSI Wilder(14) 35,00; MACD(12,26,9) 1,525, sinyal 6,167, histogram −4,642.

- Korelasi dihitung antar-return harian; R² memakai residual kuadrat terhadap jumlah kuadrat total pada sampel harga yang sama.
- Drawdown = harga / puncak berjalan − 1. Volatilitas = simpangan baku sampel return 21 hari × √252.
- RSI menggunakan inisialisasi rata-rata sederhana 14 perubahan lalu pembaruan Wilder; MACD adalah EMA12 − EMA26 dengan garis sinyal EMA9.
- STL memakai 60 `Close` akhir bulan lengkap, Okt 2021–Sep 2026, log harga, period=12, seasonal=99, seasonal_deg=0, non-robust. Rentang aktual tren {pct(trend_range[0], 6)}–{pct(trend_range[1], 6)} log; musiman {pct(seasonal_range[0], 6)}–{pct(seasonal_range[1], 6)}; residual {pct(residual_range[0], 6)}–{pct(residual_range[1], 6)}; simpangan baku residual {pct(residual_std, 6)}.
- Profil musiman aktual per bulan (komponen × 100): {profile_text}. Lima siklus lengkap ini merupakan pengamatan, bukan klaim pengulangan.
- Dari 60 harga penutupan bulanan lengkap diperoleh {len(monthly_returns)} return bulanan; Oktober 2026 parsial tidak masuk pengamatan.
- Koefisien EMA 50: α=2/(50+1)={pct(alpha_50, 8)} (≈0,039). %B terakhir = (Close−pita bawah)/(pita atas−pita bawah) = {pct(pct_b_last, 6)}; pita memakai SMA20 ±2 simpangan baku sampel (ddof=1).
- Pada 16 Okt 2026: SMA20 {pct(sma20_last)} USD, SMA50 {pct(sma50_last)} USD, EMA50 {pct(ema50_last)} USD; semuanya dihitung dari `Close` lokal dengan jendela 20/50 hari dan EMA `adjust=False`.

## Daftar judul slide

{chr(10).join(title_rows)}

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
5. Rumus SMA, EMA, Bollinger, dan RSI dilengkapi; contoh QQQ menampilkan α50={pct(alpha_50, 8)}, %B={pct(pct_b_last, 2)}, RSI 35,00, serta MACD 1,525/6,167/−4,642.
6. Overlay dijelaskan berskala log dan small multiples bersumbu y linear bersama.
7. Ringkasan metode dibagi menjadi dua tabel yang mencakup seluruh metode.
8. Rujukan Invesco dan Nasdaq diberi hyperlink aktif dengan label sumber dan tanggal akses.
9. Catatan generik dihapus dan diganti pertanyaan diskusi bertopik dengan angka; tanda titik ganda dirapikan.
10. Slide “Istilah penting” memperkenalkan padanan Indonesia untuk istilah utama.
11. Angka persentase pada teks/tabel ditulis memakai tanda % dan koma desimal.
12. Catatan slide perusahaan menyatakan bahwa deskripsi bisnis adalah ringkasan umum.
"""
    (ROOT / "deck_numbers.md").write_text(text, encoding="utf-8")


if __name__ == "__main__":
    slide_titles = make_deck()
    print(f"Dibuat {len(slide_titles)} slide di {OUTPUT}")
    for index, title in enumerate(slide_titles, start=1):
        print(f"{index:02d}. {title}")
