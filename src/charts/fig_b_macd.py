"""MACD 12/26/9 dan histogram."""
import matplotlib.pyplot as plt
from common import C_MAIN, C_ACCENT, C_GREEN, C_RED, apply_style, load_prices, save_fig, format_date_axis, decimal_comma_axis


FAST = 12
SLOW = 26
SIGNAL = 9


def main() -> None:
    """Gambar MACD, garis sinyal, histogram, dan harga terakhir."""
    apply_style()
    close = load_prices()["Close"]
    macd = close.ewm(span=FAST, adjust=False).mean() - close.ewm(span=SLOW, adjust=False).mean()
    signal = macd.ewm(span=SIGNAL, adjust=False).mean()
    hist = macd - signal
    idx = close.index[-252:]
    fig, (ax, bx) = plt.subplots(2, 1, sharex=True, gridspec_kw={"height_ratios": [2, 1]})
    ax.plot(idx, close.loc[idx], color=C_MAIN)
    ax.set(title="Harga QQQ dan MACD (12, 26, 9)", ylabel="Harga (USD)")
    bx.plot(idx, macd.loc[idx], color=C_MAIN, label="MACD")
    bx.plot(idx, signal.loc[idx], color=C_ACCENT, ls="--", label="Garis sinyal")
    bx.bar(idx, hist.loc[idx], color=[C_GREEN if value >= 0 else C_RED for value in hist.loc[idx]])
    bx.axhline(0, color="#8A94A0", lw=0.7)
    bx.set(ylabel="Nilai MACD", xlabel="Tanggal")
    bx.legend()
    format_date_axis(bx)
    for axis in fig.axes:
        decimal_comma_axis(axis)
    save_fig(fig, "18_macd.png")


if __name__ == "__main__":
    main()
