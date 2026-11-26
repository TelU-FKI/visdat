"""Gaya, palet, pemuat data, dan penyimpan gambar bersama untuk semua grafik."""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.ticker import FuncFormatter

ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data"
FIG_DIR = ROOT / "figures"

FIG_SIZE = (8, 4.5)
DPI = 200

# Palet satu tema: biru tua (utama), oranye (sorotan), abu-abu (konteks).
C_MAIN = "#1F3A5F"
C_ACCENT = "#E07A1F"
C_GREEN = "#2E8B57"
C_RED = "#C0392B"
C_GREY = "#8A94A0"
C_LIGHT = "#E6EAF0"
C_SERIES = ["#1F3A5F", "#E07A1F", "#2E8B57", "#8E44AD", "#C0392B", "#16A5B8"]

BULAN = ["Jan", "Feb", "Mar", "Apr", "Mei", "Jun", "Jul", "Agu", "Sep", "Okt", "Nov", "Des"]
HARI = ["Sen", "Sel", "Rab", "Kam", "Jum"]


def apply_style() -> None:
    plt.rcParams.update({
        "figure.figsize": FIG_SIZE,
        "figure.dpi": DPI,
        "savefig.dpi": DPI,
        "font.family": "DejaVu Sans",
        "font.size": 11,
        "axes.titlesize": 14,
        "axes.titleweight": "bold",
        "axes.titlelocation": "left",
        "axes.labelsize": 11,
        "xtick.labelsize": 10,
        "ytick.labelsize": 10,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.grid": True,
        "axes.axisbelow": True,
        "grid.color": C_LIGHT,
        "grid.linewidth": 0.8,
        "legend.frameon": False,
        "legend.fontsize": 10,
    })


def load_prices() -> pd.DataFrame:
    return pd.read_csv(DATA_DIR / "qqq_ohlcv.csv", index_col=0, parse_dates=True)


def load_constituent_closes() -> pd.DataFrame:
    return pd.read_csv(DATA_DIR / "constituents_close.csv", index_col=0, parse_dates=True)


def load_holdings() -> pd.DataFrame:
    return pd.read_csv(DATA_DIR / "holdings_top.csv")


def load_sectors() -> pd.Series:
    return pd.read_csv(DATA_DIR / "sector_weights.csv", index_col=0)["Bobot"]


def format_date_axis(ax, with_year: bool = True) -> None:
    """Sumbu tanggal berbahasa Indonesia ('Jan 2024')."""
    def _fmt(x, _pos):
        d = mdates.num2date(x)
        return f"{BULAN[d.month - 1]} {d.year}" if with_year else BULAN[d.month - 1]

    ax.xaxis.set_major_formatter(FuncFormatter(_fmt))


def fmt_id(value: float, decimals: int = 1, signed: bool = False) -> str:
    """Angka berformat Indonesia: koma desimal dan minus Unicode ('−35,6')."""
    text = f"{value:+.{decimals}f}" if signed else f"{value:.{decimals}f}"
    return text.replace(".", ",").replace("-", "−")


def decimal_comma_axis(ax, axis: str = "y") -> None:
    """Tick sumbu dengan koma desimal. axis: 'x', 'y', atau 'both'."""
    def _fmt(v, _pos):
        return f"{v:g}".replace(".", ",").replace("-", "−")

    if axis in ("y", "both"):
        ax.yaxis.set_major_formatter(FuncFormatter(_fmt))
    if axis in ("x", "both"):
        ax.xaxis.set_major_formatter(FuncFormatter(_fmt))


def plain_heatmap_axes(ax) -> None:
    """Heatmap/gambar sel: matikan grid dan spine agar sel tidak terpotong garis."""
    ax.grid(False)
    for spine in ax.spines.values():
        spine.set_visible(False)


def save_fig(fig, name: str) -> Path:
    FIG_DIR.mkdir(exist_ok=True)
    path = FIG_DIR / name
    fig.tight_layout()
    fig.savefig(path, facecolor="white")
    plt.close(fig)
    return path
