import mplfinance as mpf
import numpy as np
from common import apply_style, decimal_comma_axis, load_prices, BULAN
OUTPUT = "figures/03_candlestick.png"
HARI = 120
JUMLAH_TICK = 7
JUTA = 1_000_000


def main() -> None:
    apply_style()
    data = load_prices().tail(HARI)
    data["Volume"] = data["Volume"] / JUTA
    data.index.name = "Tanggal"
    colors = mpf.make_marketcolors(up="#2E8B57", down="#C0392B", edge="inherit", wick="inherit", volume="inherit")
    colors["vcedge"] = {"up":"#2E8B57", "down":"#C0392B"}
    style = mpf.make_mpf_style(base_mpf_style="yahoo", marketcolors=colors, y_on_right=False, rc={"axes.axisbelow": True})
    fig, axes = mpf.plot(data[["Open", "High", "Low", "Close", "Volume"]], type="candle", volume=True, style=style, figsize=(8,4.5),
                         ylabel="Harga (USD)", ylabel_lower="Volume (juta lembar)", returnfig=True)
    fig.suptitle("QQQ: candlestick dan volume (120 hari bursa)", x=.08, ha="left", fontweight="bold", fontsize=12)
    fig.subplots_adjust(left=.09, right=.98, top=.86, bottom=.16, hspace=.08)
    positions = [round(position) for position in np.linspace(0, len(data) - 1, JUMLAH_TICK)]
    ticks = [data.index[round(position)] for position in positions]
    axes[0].set_xticks(positions)
    axes[0].set_xticklabels([f"{BULAN[date.month - 1]} {date.year}" for date in ticks])
    for ax in axes:
        decimal_comma_axis(ax)
    fig.savefig(OUTPUT, dpi=200, facecolor="white")
