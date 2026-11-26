import calendar
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.colors import Normalize
from matplotlib.cm import ScalarMappable
from common import apply_style, decimal_comma_axis, load_prices, plain_heatmap_axes, save_fig, BULAN, HARI

OUTPUT = "06_heatmap_kalender.png"
ROWS = 3
COLUMNS = 4
WEEKS = 6
GRID_RATIOS = [1, 1, 1, 1, .12]


def main() -> None:
    apply_style()
    returns = load_prices()["Close"].pct_change().dropna()
    recent = returns.loc[returns.index >= returns.index.max() - pd.DateOffset(months=12)] * 100
    months = sorted(recent.index.to_period("M").unique())[-12:]
    recent = recent[recent.index.to_period("M").isin(months)]
    fig = plt.figure(figsize=(8,4.5))
    grid = fig.add_gridspec(ROWS, COLUMNS + 1, width_ratios=GRID_RATIOS, left=.035, right=.87, top=.79, bottom=.13, wspace=.10, hspace=.82)
    axes = np.array([[fig.add_subplot(grid[row, col]) for col in range(COLUMNS)] for row in range(ROWS)])
    bound = float(recent.abs().quantile(.98))
    for ax, month in zip(axes.flat, months):
        values = recent[recent.index.to_period("M") == month]
        matrix = np.full((WEEKS,5), np.nan)
        for date, value in values.items():
            first_weekday = calendar.monthrange(date.year, date.month)[0]
            week = (date.day + first_weekday - 1) // 7
            if date.weekday() < 5:
                matrix[week, date.weekday()] = value
        ax.imshow(matrix, cmap="RdYlGn", vmin=-bound, vmax=bound, aspect="auto")
        plain_heatmap_axes(ax)
        ax.set(title=f"{BULAN[month.month-1]} {month.year}", xticks=range(5), xticklabels=HARI, yticks=[])
        ax.title.set_fontsize(12)
        ax.tick_params(axis="x", labelsize=9, pad=3)
    fig.suptitle("Kalender return harian QQQ", x=.08, y=.98, ha="left", fontweight="bold")
    fig.text(.08, .895, "Data s.d. 16 Okt 2026; Okt 2026 belum lengkap", fontsize=11)
    mapper = ScalarMappable(norm=Normalize(-bound, bound), cmap="RdYlGn")
    color_axis = fig.add_subplot(grid[:, COLUMNS])
    color_axis.set_in_layout(False)
    colorbar = fig.colorbar(mapper, cax=color_axis)
    colorbar.set_label("Return harian (%)")
    decimal_comma_axis(colorbar.ax)
    save_fig(fig, OUTPUT)
