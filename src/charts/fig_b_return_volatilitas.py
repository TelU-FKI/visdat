"""Return harian dan volatilitas bergulir tahunan."""
import matplotlib.pyplot as plt
from common import C_MAIN, C_ACCENT, apply_style, load_prices, save_fig, format_date_axis, decimal_comma_axis


WINDOW = 21
TRADING_DAYS = 252


def main() -> None:
    """Gambar return harian dan volatilitas 21 hari yang dianualisasi."""
    apply_style()
    close = load_prices()["Close"]
    returns = close.pct_change()
    volatility = returns.rolling(WINDOW).std() * TRADING_DAYS ** 0.5
    fig, (ax, bx) = plt.subplots(2, 1, sharex=True)
    ax.plot(returns.index, returns * 100, color=C_MAIN, lw=0.65)
    ax.axhline(0, color=C_ACCENT, lw=0.8)
    ax.set(title="Return harian dan volatilitas bergulir", ylabel="Return (%)")
    bx.plot(volatility.index, volatility * 100, color=C_ACCENT)
    bx.set(ylabel="Volatilitas tahunan (%)", xlabel="Tanggal")
    format_date_axis(bx)
    for axis in fig.axes:
        decimal_comma_axis(axis)
    save_fig(fig, "15_return_volatilitas.png")


if __name__ == "__main__":
    main()
