from fig_a_00_harga_vs_return import main as fig00
from fig_a_01_line_close import main as fig01
from fig_a_02_area_volume import main as fig02
from fig_a_03_candlestick import main as fig03
from fig_a_04_seasonal_plot import main as fig04
from fig_a_05_heatmap_bulanan import main as fig05
from fig_a_06_heatmap_kalender import main as fig06
from fig_a_07_multi_overlay import main as fig07
from fig_a_08_multi_small import main as fig08
from fig_a_09_korelasi import main as fig09
from fig_a_19_sektor import main as fig19
from fig_a_20_top_holdings import main as fig20

FIGURES = [fig00, fig01, fig02, fig03, fig04, fig05, fig06, fig07, fig08, fig09, fig19, fig20]


def main() -> None:
    for make_figure in FIGURES:
        make_figure()


if __name__ == "__main__":
    main()
