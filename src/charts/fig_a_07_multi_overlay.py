import matplotlib.pyplot as plt
from common import C_SERIES, apply_style, decimal_comma_axis, format_date_axis, load_constituent_closes, load_prices, save_fig

OUTPUT = "07_multi_overlay.png"


def main() -> None:
    apply_style()
    constituents = load_constituent_closes()
    data = load_prices()[["Close"]].join(constituents.iloc[:, :5], how="inner")
    data.columns = ["QQQ", *data.columns[1:]]
    indexed = data.div(data.iloc[0]).mul(100)
    fig, ax = plt.subplots()
    for i, name in enumerate(indexed.columns):
        ax.semilogy(indexed.index, indexed[name], color=C_SERIES[i % len(C_SERIES)], lw=1, label=name)
    ax.set(title="Perbandingan kinerja: indeks awal = 100", ylabel="Indeks (awal = 100, skala log)", xlabel="Tanggal")
    ax.legend(ncol=3)
    format_date_axis(ax)
    decimal_comma_axis(ax)
    save_fig(fig, OUTPUT)
