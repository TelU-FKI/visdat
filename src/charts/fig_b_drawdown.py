"""Underwater plot drawdown harga QQQ."""
import matplotlib.pyplot as plt
from common import C_MAIN, C_ACCENT, BULAN, fmt_id, decimal_comma_axis
from common import apply_style, load_prices, save_fig, format_date_axis


def main() -> None:
    """Tandai drawdown maksimum dengan anotasi berpemanah."""
    apply_style()
    close = load_prices()["Close"]
    drawdown = close / close.cummax() - 1
    trough = drawdown.idxmin()
    value = drawdown.loc[trough] * 100
    fig, ax = plt.subplots()
    ax.fill_between(drawdown.index, drawdown * 100, 0, color="#DCE4ED")
    ax.plot(drawdown.index, drawdown * 100, color=C_MAIN, lw=0.9)
    ax.scatter([trough], [value], color=C_ACCENT, zorder=3)
    label = f"Maksimum {fmt_id(value, 1, signed=True)}%\n{trough.day} {BULAN[trough.month - 1]} {trough.year}"
    ax.annotate(label, xy=(trough, value), xytext=(35, 35), textcoords="offset points",
                arrowprops={"arrowstyle": "->", "color": C_ACCENT}, color=C_ACCENT)
    ax.set(title="Drawdown QQQ dari puncak sebelumnya", ylabel="Drawdown (%)")
    decimal_comma_axis(ax)
    format_date_axis(ax)
    save_fig(fig, "16_drawdown.png")


if __name__ == "__main__":
    main()
