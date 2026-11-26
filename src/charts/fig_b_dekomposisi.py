"""Dekomposisi STL bulanan dan profil musiman QQQ."""
import numpy as np
import matplotlib.pyplot as plt
from statsmodels.tsa.seasonal import STL
from common import (BULAN, C_GREEN, C_RED, apply_style, decimal_comma_axis,
                    fmt_id, format_date_axis, load_prices, save_fig)


PERIOD = 12
SEASONAL_WINDOW = 99


def stl_components():
    """Fit STL pada lima siklus lengkap, dari Okt 2021 sampai Sep 2026."""
    monthly = load_prices()["Close"].resample("ME").last().iloc[:-1]
    log_price = np.log(monthly)
    result = STL(log_price, period=PERIOD, seasonal=SEASONAL_WINDOW,
                 seasonal_deg=0).fit()
    return log_price, result


def main() -> None:
    """Gambar empat komponen STL pada log harga akhir bulan."""
    apply_style()
    log_price, result = stl_components()
    fig, axes = plt.subplots(4, 1, figsize=(8, 4.5), sharex=True)
    parts = [(log_price, "Observasi"), (result.trend, "Tren"),
             (result.seasonal, "Musiman"), (result.resid, "Residual")]
    for ax, (series, label) in zip(axes, parts):
        ax.plot(series.index, series, lw=1.0)
        ax.set_ylabel(label)
        decimal_comma_axis(ax)
    seasonal_limit = max(abs(result.seasonal).max(), abs(result.resid).max()) * 1.15
    axes[2].set_ylim(-seasonal_limit, seasonal_limit)
    axes[3].set_ylim(-seasonal_limit, seasonal_limit)
    axes[0].set_title("Dekomposisi STL pada log harga QQQ", pad=30)
    axes[0].text(0, 1.04, "Okt 2021-Sep 2026, 60 bulan; STL periode 12, musiman periodik",
                 transform=axes[0].transAxes, fontsize=10, va="bottom")
    axes[-1].set_xlabel("Tanggal")
    format_date_axis(axes[-1])
    save_fig(fig, "14_dekomposisi.png")


def main_profile() -> None:
    """Buat batang profil komponen musiman rata-rata per bulan."""
    apply_style()
    _, result = stl_components()
    profile = (result.seasonal.groupby(result.seasonal.index.month).mean() * 100)
    values = profile.reindex(range(1, 13)).to_numpy()
    colors = [C_GREEN if value >= 0 else C_RED for value in values]
    fig, ax = plt.subplots()
    bars = ax.bar(BULAN, values, color=colors)
    ax.axhline(0, color="#555555", lw=0.8)
    for bar, value in zip(bars, values):
        offset = 0.15 if value >= 0 else -0.15
        ax.text(bar.get_x() + bar.get_width() / 2, value + offset,
                f"{fmt_id(value, 1, signed=True)}%", ha="center",
                va="bottom" if value >= 0 else "top", fontsize=10)
    ax.set(title="Profil musiman bulanan QQQ",
           ylabel="Komponen musiman (log x 100, kira-kira %)",
           ylim=(min(values) - 0.8, max(values) + 0.7))
    ax.text(0.99, 0.97, "Okt 2021-Sep 2026, 60 bulan", transform=ax.transAxes,
            fontsize=10, va="top", ha="right",
            bbox={"facecolor": "white", "edgecolor": "none", "alpha": 0.85})
    ax.tick_params(axis="x", labelrotation=30)
    for label in ax.get_xticklabels():
        label.set_ha("right")
    decimal_comma_axis(ax)
    save_fig(fig, "14b_profil_musiman.png")


if __name__ == "__main__":
    main()
