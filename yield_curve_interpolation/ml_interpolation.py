import numpy as np

from sklearn.gaussian_process import GaussianProcessRegressor


def gaussian_process_interpolation(rate: np.array,
                                   maturities: np.array) -> callable:
    """
    Perform Gaussian Process interpolation on the given rates to estimate yields at target maturities.
    Parameters
    ----------
    rate : np.array
        Rates at known maturities.
    maturities : np.array
        Maturities corresponding to the yield curves.
    Returns
    -------
    Callable
        Estimated yields at the target maturities.
    """

    gp = GaussianProcessRegressor()
    gp.fit(maturities.reshape(-1, 1), rate)

    def interpolate(target_maturities: np.array) -> np.array:
        estimated_yields = gp.predict(target_maturities.reshape(-1, 1))
        return estimated_yields

    return interpolate


