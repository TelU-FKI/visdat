"""Bollinger Bands 20 hari dengan dua simpangan baku sampel."""
import matplotlib.pyplot as plt
from common import C_MAIN, C_ACCENT, C_LIGHT, apply_style, load_prices, save_fig, format_date_axis, decimal_comma_axis


WINDOW = 20
DEVIATIONS = 2


def main() -> None:
    """Gambar pita Bollinger dan persentase B."""
    apply_style()
    close = load_prices()["Close"]
    mean = close.rolling(WINDOW).mean()
    std = close.rolling(WINDOW).std(ddof=1)
    upper, lower = mean + DEVIATIONS * std, mean - DEVIATIONS * std
    pct_b = (close - lower) / (upper - lower)
    idx = close.index[-252:]
    fig, (ax, bx) = plt.subplots(2, 1, sharex=True, gridspec_kw={"height_ratios": [3, 1]})
    ax.plot(idx, close.loc[idx], color=C_MAIN, label="Harga penutupan")
    ax.plot(idx, mean.loc[idx], color=C_ACCENT, label="Rata-rata 20 hari")
    ax.plot(idx, upper.loc[idx], color=C_MAIN, ls="--", label="Pita atas (+2σ)")
    ax.plot(idx, lower.loc[idx], color=C_MAIN, ls=":", label="Pita bawah (−2σ)")
    ax.fill_between(idx, lower.loc[idx], upper.loc[idx], color=C_LIGHT, alpha=0.65)
    ax.set(title="Bollinger Bands 20 hari (±2 simpangan baku)", ylabel="Harga (USD)")
    ax.legend(ncol=2)
    bx.plot(idx, pct_b.loc[idx], color=C_ACCENT, label="%B")
    bx.axhline(1, color=C_MAIN, ls="--"); bx.axhline(0, color=C_MAIN, ls=":")
    bx.set(ylabel="%B", xlabel="Tanggal")
    format_date_axis(bx)
    for axis in fig.axes:
        decimal_comma_axis(axis)
    save_fig(fig, "12_bollinger.png")


if __name__ == "__main__":
    main()
