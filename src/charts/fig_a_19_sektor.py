import matplotlib.pyplot as plt
from common import C_MAIN, apply_style, decimal_comma_axis, fmt_id, load_sectors, save_fig

OUTPUT = "19_sektor.png"
TERJEMAHAN = {"realestate":"Properti", "consumer_cyclical":"Konsumsi Siklikal", "basic_materials":"Bahan Baku", "consumer_defensive":"Konsumsi Defensif", "technology":"Teknologi", "communication_services":"Layanan Komunikasi", "financial_services":"Jasa Keuangan", "utilities":"Utilitas", "industrials":"Industri", "energy":"Energi", "healthcare":"Kesehatan"}


def main() -> None:
    apply_style()
    weights = load_sectors().sort_values()
    labels = [TERJEMAHAN.get(key, key) for key in weights.index]
    fig, ax = plt.subplots(figsize=(8,4.5))
    bars = ax.barh(labels, weights.values * 100, color=C_MAIN)
    ax.bar_label(bars, labels=[f"{fmt_id(value, 1)}%" for value in weights.values * 100], padding=3, fontsize=10)
    ax.set(title="Bobot sektor dalam QQQ", xlabel="Bobot (%)")
    ax.set_xlim(0, max(weights.values * 100) * 1.18)
    ax.set_axisbelow(True)
    ax.yaxis.grid(False)
    ax.xaxis.grid(True)
    decimal_comma_axis(ax, axis="x")
    save_fig(fig, OUTPUT)
