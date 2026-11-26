"""Pencocokan model tren terhadap harga QQQ."""
import numpy as np
import matplotlib.pyplot as plt
from common import C_MAIN, C_ACCENT, C_GREEN, fmt_id, apply_style, load_prices, save_fig, format_date_axis, decimal_comma_axis


def main() -> None:
    """Pasang model linear, polinomial kubik, dan eksponensial."""
    apply_style()
    y = load_prices()["Close"].to_numpy()
    x = np.arange(len(y), dtype=float)
    fits = [("Linear", np.polyval(np.polyfit(x, y, 1), x), C_MAIN),
            ("Polinomial derajat 3", np.polyval(np.polyfit(x, y, 3), x), C_ACCENT)]
    logfit = np.polyval(np.polyfit(x, np.log(y), 1), x)
    fits.append(("Eksponensial (regresi pada log harga)", np.exp(logfit), C_GREEN))
    fig, ax = plt.subplots()
    ax.plot(load_prices().index, y, color="#8A94A0", lw=0.8, label="Harga aktual")
    for label, fitted, color in fits:
        r2 = 1 - np.sum((y - fitted) ** 2) / np.sum((y - y.mean()) ** 2)
        ax.plot(load_prices().index, fitted, color=color, label=f"{label} (R²={fmt_id(r2, 4)})")
    ax.set(title="Pencocokan tren harga QQQ", ylabel="Harga (USD)")
    ax.text(0.99, 0.02, "R² dihitung pada skala harga", transform=ax.transAxes,
            ha="right", va="bottom", fontsize=10,
            bbox={"facecolor": "white", "edgecolor": "none", "alpha": 0.8})
    ax.legend()
    format_date_axis(ax)
    for axis in fig.axes:
        decimal_comma_axis(axis)
    save_fig(fig, "13_fitting.png")


if __name__ == "__main__":
    main()
