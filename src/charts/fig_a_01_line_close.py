import matplotlib.pyplot as plt
from common import C_MAIN, apply_style, decimal_comma_axis, format_date_axis, load_prices, save_fig

OUTPUT = "01_line_close.png"


def main() -> None:
    apply_style()
    data = load_prices()
    fig, ax = plt.subplots()
    ax.plot(data.index, data["Close"], color=C_MAIN, lw=1.1, label="Harga penutupan")
    ax.set(title="Harga penutupan QQQ selama lima tahun", ylabel="Harga (USD)", xlabel="Tanggal")
    ax.legend()
    format_date_axis(ax)
    decimal_comma_axis(ax)
    save_fig(fig, OUTPUT)
