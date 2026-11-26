import matplotlib.pyplot as plt
from common import C_SERIES, apply_style, decimal_comma_axis, load_prices, save_fig, BULAN

OUTPUT = "04_seasonal_plot.png"
BASE_YEAR = 2021
BASE_MONTH = 10
PARALLEL_YEARS = {2021, 2026}
FINAL_YEAR = 2026


def main() -> None:
    apply_style()
    close = load_prices()["Close"]
    month_close = close.resample("ME").last().iloc[:-1]
    monthly = month_close.pct_change().dropna()
    fig, ax = plt.subplots()
    years = sorted(month_close.index.year.unique())
    for i, year in enumerate(years):
        points = monthly[monthly.index.year == year]
        if year == BASE_YEAR:
            points = points[points.index.month > BASE_MONTH]
        values = (1 + points).cumprod().sub(1) * 100
        partial = year in PARALLEL_YEARS
        label = f"{year} parsial (Nov–Des)" if year == BASE_YEAR else f"{year} parsial (Jan–Sep)" if year == FINAL_YEAR else str(year)
        ax.plot(points.index.month, values, color=C_SERIES[i % len(C_SERIES)], marker="o", ms=4,
                linestyle="--" if partial else "-", label=label)
    ax.set(title="Return kumulatif bulanan QQQ", xlabel="Bulan — Okt 2026 (s.d. 16 Okt) tidak ditampilkan",
           ylabel="Imbal hasil kumulatif (%)", xticks=range(1,13), xticklabels=BULAN)
    ax.legend(ncol=3, fontsize=10)
    decimal_comma_axis(ax)
    save_fig(fig, OUTPUT)
