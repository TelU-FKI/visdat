import matplotlib.pyplot as plt
import pandas as pd
from common import C_MAIN, apply_style, decimal_comma_axis, fmt_id, load_constituent_closes, load_prices, plain_heatmap_axes, save_fig

OUTPUT = "09_korelasi.png"


def main() -> None:
    apply_style()
    closes = load_constituent_closes()
    data = load_prices()[["Close"]].join(closes, how="inner")
    data = data.rename(columns={"Close":"QQQ"})
    corr = data.pct_change().dropna().corr()
    fig, ax = plt.subplots(figsize=(8,4.5))
    image = ax.imshow(corr, vmin=0, vmax=1, cmap="Blues")
    plain_heatmap_axes(ax)
    labels = corr.columns.tolist()
    ax.set(title="Korelasi return QQQ dan 10 holding", xticks=range(len(labels)), yticks=range(len(labels)), xticklabels=labels, yticklabels=labels)
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right", fontsize=10)
    for row in range(len(labels)):
        for col in range(len(labels)):
            value = corr.iloc[row,col]
            ax.text(col, row, fmt_id(value, 2), ha="center", va="center", fontsize=9, color="white" if value >= .6 else C_MAIN)
    colorbar = fig.colorbar(image, ax=ax, label="Korelasi")
    decimal_comma_axis(colorbar.ax)
    save_fig(fig, OUTPUT)
