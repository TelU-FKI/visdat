import matplotlib.pyplot as plt
from common import C_MAIN, C_ACCENT, apply_style, decimal_comma_axis, load_prices, save_fig

OUTPUT = "00_harga_vs_return.png"


def main() -> None:
    apply_style()
    data = load_prices()
    returns = data["Close"].pct_change() * 100
    fig, axes = plt.subplots(2, 1, figsize=(8, 4.5), sharex=True)
    axes[0].plot(data.index, data["Close"], color=C_MAIN, lw=1)
    axes[0].set(title="Harga penutupan QQQ", ylabel="Harga (USD)")
    axes[1].plot(returns.index, returns, color=C_ACCENT, lw=.6)
    axes[1].axhline(0, color=C_MAIN, lw=.8)
    axes[1].set(title="Return harian QQQ", ylabel="Return (%)", xlabel="Tanggal")
    for ax in axes:
        decimal_comma_axis(ax)
    save_fig(fig, OUTPUT)
