import matplotlib.pyplot as plt
from common import C_MAIN, C_ACCENT, apply_style, decimal_comma_axis, format_date_axis, load_prices, save_fig

OUTPUT = "02_area_volume.png"
JUTA = 1_000_000
JENDELA = 21


def main() -> None:
    apply_style()
    data = load_prices()
    volume = data["Volume"] / JUTA
    fig, ax = plt.subplots()
    ax.fill_between(data.index, volume, color=C_MAIN, alpha=.28, label="Volume harian")
    ax.plot(data.index, volume.rolling(JENDELA).mean(), color=C_ACCENT, lw=1.4, label="Rata-rata 21 hari")
    ax.set(title="Volume perdagangan QQQ", ylabel="Volume (juta lembar)", xlabel="Tanggal")
    ax.legend()
    format_date_axis(ax)
    decimal_comma_axis(ax)
    save_fig(fig, OUTPUT)
