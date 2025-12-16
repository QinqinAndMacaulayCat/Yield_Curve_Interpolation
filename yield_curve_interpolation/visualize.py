"""
Visualize yield curve
"""

from matplotlib import pyplot as plt
import numpy as np

def plot_yield_curve(maturities: np.array,
                     data: np.array = None,
                     key_maturities: np.array = None,
                     key_data: np.array = None,
                     title: str = "Yield Curve",
                     xlabel: str = "Maturities",
                     ylabel: str = "zero_rate",
                     show_dots: bool = True,
                     save_path: str = None) -> None:
    """
    Plot the yield curve based on given maturities and rates or discount factors.

    Parameters
    ----------
    maturities : np.array
        Array of maturities.
    data : np.array, optional
        Title of the plot.
    xlabel : str, optional
        Label for the x-axis.
    ylabel : str, optional
        Label for the y-axis. Select from "zero_rate", "forward_rate", "discount_factor", "rt".
    show_dots : bool, optional
        Whether to show dots on the curve.
    save_path : str, optional
        Path to save the plot.
    Returns
    -------
    None
    """

    plt.figure(figsize=(10, 6))

    plt.plot(maturities, data, label="Zero Rates")
    if show_dots and key_maturities is not None and key_data is not None:
        plt.scatter(key_maturities, key_data, color='red', label='Key Points', zorder=5)
    plt.ylabel(ylabel)

    plt.title(title)
    plt.xlabel(xlabel)
    plt.grid(True)
    plt.legend()
    if save_path:
        plt.savefig(save_path)