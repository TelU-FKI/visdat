"""Harga QQQ dengan rata-rata bergerak sederhana."""
import matplotlib.pyplot as plt
from common import C_MAIN, C_ACCENT, C_GREEN, apply_style, load_prices, save_fig, format_date_axis, decimal_comma_axis


def main() -> None:
    """Gambar SMA 20, 50, dan 200 hari."""
    apply_style()
    data = load_prices()
    close = data["Close"]
    fig, ax = plt.subplots()
    ax.plot(close.index, close, color=C_MAIN, lw=1.1, label="Harga penutupan")
    for window, color in [(20, C_ACCENT), (50, C_GREEN), (200, "#8E44AD")]:
        ax.plot(close.index, close.rolling(window).mean(), color=color,
                label=f"SMA {window} hari")
    ax.set(title="Harga QQQ dan rata-rata bergerak sederhana", ylabel="Harga (USD)")
    ax.legend(ncol=2)
    format_date_axis(ax)
    for axis in fig.axes:
        decimal_comma_axis(axis)
    save_fig(fig, "10_sma.png")


if __name__ == "__main__":
    main()
