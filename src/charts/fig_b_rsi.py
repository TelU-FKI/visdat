"""Harga dan RSI Wilder 14 hari."""
import pandas as pd
import matplotlib.pyplot as plt
from common import C_MAIN, C_ACCENT, apply_style, load_prices, save_fig, format_date_axis, decimal_comma_axis


PERIOD = 14


def wilder_rsi(close: pd.Series) -> pd.Series:
    """Hitung RSI dengan rata-rata awal sederhana dan pemulusan Wilder."""
    change = close.diff()
    gains, losses = change.clip(lower=0), -change.clip(upper=0)
    avg_gain = pd.Series(float("nan"), index=close.index)
    avg_loss = avg_gain.copy()
    avg_gain.iloc[PERIOD] = gains.iloc[1:PERIOD + 1].mean()
    avg_loss.iloc[PERIOD] = losses.iloc[1:PERIOD + 1].mean()
    for i in range(PERIOD + 1, len(close)):
        avg_gain.iloc[i] = (avg_gain.iloc[i - 1] * (PERIOD - 1) + gains.iloc[i]) / PERIOD
        avg_loss.iloc[i] = (avg_loss.iloc[i - 1] * (PERIOD - 1) + losses.iloc[i]) / PERIOD
    rs = avg_gain / avg_loss
    return 100 - 100 / (1 + rs)


def main() -> None:
    """Gambar RSI dengan garis 30 dan 70."""
    apply_style()
    close = load_prices()["Close"]
    rsi = wilder_rsi(close)
    idx = close.index[-252:]
    fig, (ax, bx) = plt.subplots(2, 1, sharex=True, gridspec_kw={"height_ratios": [2, 1]})
    ax.plot(idx, close.loc[idx], color=C_MAIN)
    ax.set(title="Harga QQQ dan RSI Wilder 14 hari", ylabel="Harga (USD)")
    bx.plot(idx, rsi.loc[idx], color=C_ACCENT, label="RSI 14")
    bx.axhline(70, color=C_MAIN, ls="--", label="Batas 70")
    bx.axhline(30, color=C_MAIN, ls=":", label="Batas 30")
    bx.set(ylabel="RSI", xlabel="Tanggal", ylim=(0, 100))
    bx.legend(ncol=3)
    format_date_axis(bx)
    for axis in fig.axes:
        decimal_comma_axis(axis)
    save_fig(fig, "17_rsi.png")


if __name__ == "__main__":
    main()
