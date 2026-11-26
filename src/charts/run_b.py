"""Jalankan pembuat grafik bagian kedua."""
from fig_b_sma import main as sma
from fig_b_ema_vs_sma import main as ema_vs_sma
from fig_b_bollinger import main as bollinger
from fig_b_fitting import main as fitting
from fig_b_dekomposisi import main as dekomposisi, main_profile as profil_musiman
from fig_b_return_volatilitas import main as return_volatilitas
from fig_b_drawdown import main as drawdown
from fig_b_rsi import main as rsi
from fig_b_macd import main as macd


CHARTS = [sma, ema_vs_sma, bollinger, fitting, dekomposisi, profil_musiman,
          return_volatilitas, drawdown, rsi, macd]


def main() -> None:
    """Buat semua grafik 10 sampai 18."""
    for chart in CHARTS:
        chart()


if __name__ == "__main__":
    main()
