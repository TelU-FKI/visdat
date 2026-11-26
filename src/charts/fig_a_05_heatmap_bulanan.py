import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.colors import TwoSlopeNorm
from common import apply_style, decimal_comma_axis, load_prices, plain_heatmap_axes, save_fig, BULAN

OUTPUT = "05_heatmap_bulanan.png"


def main() -> None:
    apply_style()
    close = load_prices()["Close"]
    month_close = close.resample("ME").last().iloc[:-1]
    monthly = month_close.pct_change().dropna() * 100
    table = monthly.to_frame("return")
    table["Tahun"], table["Bulan"] = table.index.year, table.index.month
    grid = table.pivot(index="Tahun", columns="Bulan", values="return").reindex(columns=range(1,13))
    bound = max(abs(grid.min().min()), abs(grid.max().max()))
    fig, ax = plt.subplots(figsize=(8,4.5))
    image = ax.imshow(grid, aspect="auto", cmap="RdYlGn", norm=TwoSlopeNorm(vmin=-bound, vcenter=0, vmax=bound))
    plain_heatmap_axes(ax)
    years = [f"{year} (parsial)" if year in {2021, 2026} else str(year) for year in grid.index]
    ax.set(title="Return bulanan QQQ", xlabel="Bulan", ylabel="Tahun", xticks=range(12), xticklabels=BULAN, yticks=range(len(grid)), yticklabels=years)
    colorbar = fig.colorbar(image, ax=ax, label="Return (%)")
    decimal_comma_axis(colorbar.ax)
    save_fig(fig, OUTPUT)
