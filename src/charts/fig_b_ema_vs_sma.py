"""Perbandingan EMA dan SMA pada satu tahun terakhir."""
import matplotlib.pyplot as plt
from common import C_MAIN, C_ACCENT, apply_style, load_prices, save_fig, format_date_axis, decimal_comma_axis


WINDOW = 50


def main() -> None:
    """Gambar EMA 50 dan SMA 50 beserta harga."""
    apply_style()
    close = load_prices()["Close"]
    recent = close.iloc[-252:]
    ema = close.ewm(span=WINDOW, adjust=False).mean().reindex(recent.index)
    sma = close.rolling(WINDOW).mean().reindex(recent.index)
    fig, ax = plt.subplots()
    ax.plot(recent.index, recent, color="#8A94A0", lw=0.8, label="Harga penutupan")
    ax.plot(recent.index, ema, color=C_ACCENT, label="EMA 50 (lebih responsif)")
    ax.plot(recent.index, sma, color=C_MAIN, ls="--", label="SMA 50 (lebih berjeda)")
    ax.set(title="EMA dan SMA 50 hari: respons dan jeda", ylabel="Harga (USD)")
    ax.legend()
    format_date_axis(ax)
    for axis in fig.axes:
        decimal_comma_axis(axis)
    save_fig(fig, "11_ema_vs_sma.png")


if __name__ == "__main__":
    main()
