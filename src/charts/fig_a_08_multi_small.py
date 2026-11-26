import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from common import C_SERIES, apply_style, decimal_comma_axis, format_date_axis, load_constituent_closes, load_prices, save_fig

OUTPUT = "08_multi_small.png"
Y_MARGIN = 1.08


def main() -> None:
    apply_style()
    constituents = load_constituent_closes()
    data = load_prices()[["Close"]].join(constituents.iloc[:, :5], how="inner")
    data = data.rename(columns={"Close": "QQQ"})
    indexed = data.div(data.iloc[0]).mul(100)
    fig, axes = plt.subplots(3, 2, figsize=(8,4.5), sharex=True, sharey=True)
    y_max = float(indexed.max().max()) * Y_MARGIN
    axes[0, 0].set_ylim(0, y_max)
    for i, (ax, name) in enumerate(zip(axes.flat, indexed.columns)):
        ax.plot(indexed.index, indexed[name], color=C_SERIES[i % len(C_SERIES)], lw=1)
        ax.set(title=name, ylabel="Indeks" if i % 2 == 0 else "")
        ax.set_yscale("linear")
        format_date_axis(ax)
        ax.xaxis.set_major_locator(mdates.YearLocator(2))
        ax.tick_params(axis="x", labelrotation=30, labelsize=10)
        ax.tick_params(axis="y", labelleft=i % 2 == 0, labelsize=10)
        decimal_comma_axis(ax)
    axes[-1,0].set_xlabel("Tanggal")
    axes[-1,1].set_xlabel("Tanggal")
    fig.suptitle("QQQ dan lima holding terbesar (awal = 100)", x=.08, ha="left", fontweight="bold")
    save_fig(fig, OUTPUT)
