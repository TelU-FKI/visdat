import matplotlib.pyplot as plt
from common import C_MAIN, apply_style, decimal_comma_axis, fmt_id, load_holdings, save_fig

OUTPUT = "20_top_holdings.png"


def main() -> None:
    apply_style()
    data = load_holdings().sort_values("Holding Percent").tail(10)
    labels = [f"{row.Symbol} — {row.Name}" for row in data.itertuples()]
    values = data["Holding Percent"].to_numpy() * 100
    fig, ax = plt.subplots(figsize=(8,4.5))
    bars = ax.barh(labels, values, color=C_MAIN)
    ax.bar_label(bars, labels=[f"{fmt_id(value, 2)}%" for value in values], padding=3, fontsize=10)
    ax.set(title="10 holding terbesar QQQ", xlabel="Bobot (%)")
    ax.set_xlim(0, max(values) * 1.22)
    ax.set_axisbelow(True)
    ax.yaxis.grid(False)
    ax.xaxis.grid(True)
    decimal_comma_axis(ax, axis="x")
    save_fig(fig, OUTPUT)
