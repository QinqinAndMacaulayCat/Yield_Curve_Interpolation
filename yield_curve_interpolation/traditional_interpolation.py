"""
Traditional interpolation methods for yield curve estimation. 

"""

import numpy as np
from scipy.interpolate import CubicSpline, CubicHermiteSpline, PchipInterpolator

from scipy.optimize import curve_fit

def linear_interpolation(dfs: np.array,
                         maturities: np.array) -> callable:
    """
    Perform linear interpolation on the given discount factors to estimate yields at target maturities.
    Parameters
    ----------
    dfs : np.array
        Discount factors or yields at known maturities.
    maturities : np.array
        Maturities corresponding to the yield curves.
    Returns
    -------
    Callable
        Estimated yields at the target maturities.
    """

    RT = -np.log(dfs) 

    def interpolate(target_maturities: np.array) -> np.array:
        estimated_RT = np.interp(target_maturities, maturities, RT)
        estimated_yields = estimated_RT / target_maturities
        return estimated_yields

    return interpolate



def cubic_spline_interpolation(zero_rates: np.array,
                               maturities: np.array) -> callable:
    """
    Perform cubic spline interpolation on the given zero rates to estimate yields at target maturities.
    Parameters
    ----------
    zero_rates : np.array
        Zero rates at known maturities.
    maturities : np.array
        Maturities corresponding to the yield curves.
    target_maturities : np.array
        Target maturities for which to estimate yields.

    Returns
    -------
    Callable
        Estimated yields at the target maturities.
    """


    cs = CubicSpline(maturities, zero_rates)

    return cs


def Hermite_interpolation(dfs: np.array,
                          maturities: np.array) -> callable:
    """
    Perform Hermite interpolation on the given discount factors to estimate yields at target maturities.
    Parameters
    ----------
    dfs : np.array
        Discount factors or yields at known maturities.
    maturities : np.array
        Maturities corresponding to the yield curves.
    target_maturities : np.array
        Target maturities for which to estimate yields.

    Returns
    -------
    Callable
        Estimated yields at the target maturities.
    """

    dfs = np.asarray(dfs, dtype=float)
    maturities = np.asarray(maturities, dtype=float)

    if np.any(np.diff(maturities) <= 0):
        raise ValueError("maturities must be strictly increasing")

    f_intervals = -(np.diff(np.log(dfs)) / np.diff(maturities))  # size n-1

    f_nodes = np.empty_like(dfs)
    f_nodes[0] = f_intervals[0]
    f_nodes[-1] = f_intervals[-1]
    if len(dfs) > 2:
        f_nodes[1:-1] = 0.5 * (f_intervals[:-1] + f_intervals[1:])

    dP_dt = -f_nodes * dfs

    spline = CubicHermiteSpline(maturities, dfs, dP_dt)

    def interpolate_(target_maturities: np.ndarray) -> np.ndarray:
        target_maturities = np.asarray(target_maturities, dtype=float)
        P_t = spline(target_maturities)

        eps = 1e-12
        P_t = np.clip(P_t, eps, None)

        y = np.empty_like(P_t)
        mask_nonzero = target_maturities > 0
        y[mask_nonzero] = -np.log(P_t[mask_nonzero]) / target_maturities[mask_nonzero]

        if np.any(~mask_nonzero):
            y[~mask_nonzero] = f_nodes[0]

        return y

    return interpolate_


def monotone_convex_interpolation(zero_rates: np.array,
                                 maturities: np.array) -> callable:
    """
    Perform monotone convex interpolation on the given zero rates to estimate yields at target maturities.
    Parameters
    ----------
    zero_rates : np.array
        Zero rates at known maturities.
    maturities : np.array
        Maturities corresponding to the yield curves.
    target_maturities : np.array
        Target maturities for which to estimate yields.

    Returns
    -------
    Callable
        Estimated yields at the target maturities.
    """


    pchip = PchipInterpolator(maturities, zero_rates)

    def interpolate_(target_maturities: np.array) -> np.array:
        estimated_yields = pchip(target_maturities)
        return estimated_yields

    return interpolate_


def Nelson_Siegel_interpolation(zero_rates: np.array,
                                maturities: np.array) -> callable:
    """
    Perform Nelson-Siegel interpolation on the given zero rates to estimate yields at target maturities.
    Parameters
    ----------
    zero_rates : np.array
        Zero rates at known maturities.
    maturities : np.array
        Maturities corresponding to the yield curves.
    Returns
    -------
    Callable
        Estimated yields at the target maturities.
    """
    # Avoid division by zero for t=0
    maturities = np.array(maturities)
    zero_rates = np.array(zero_rates)

    def nelson_siegel(t, beta0, beta1, beta2, tau):
        t = np.array(t)
        x = t / tau
        # Handle t=0 limit: lim x->0 (1-e^{-x})/x = 1
        factor = np.where(t == 0, 1.0, (1 - np.exp(-x)) / x)
        return beta0 + beta1 * factor + beta2 * (factor - np.exp(-x))

    # Fit with bounds to ensure reasonable parameters
    params, _ = curve_fit(
        nelson_siegel,
        maturities,
        zero_rates,
        bounds=([ -5, -5, -5, 1e-6], [20, 20, 20, 10]),
        maxfev=20000
    )

    def interpolate_(target_maturities: np.array) -> np.array:
        return nelson_siegel(target_maturities, *params)

    return interpolate_

def _load_ns_component(t, tau):
    """Stable computation of (1 - exp(-t/tau)) / (t/tau)."""
    x = t / tau
    # use Taylor expansion for small x to avoid division by zero
    return np.where(x < 1e-6, 1 - x/2 + x**2/6, (1 - np.exp(-x)) / x)


def Svensson_interpolation(zero_rates: np.array,
                           maturities: np.array) -> callable:
    """
    Fit the Nelson-Siegel-Svensson zero rate curve and return an interpolating function.
    """

    # Ensure numpy arrays & sorted (important for curve_fit stability)
    maturities = np.asarray(maturities).astype(float)
    zero_rates = np.asarray(zero_rates)
    sort_idx = np.argsort(maturities)
    maturities = maturities[sort_idx]
    zero_rates = zero_rates[sort_idx]

    # Svensson zero rate formula
    def svensson(maturity, beta0, beta1, beta2, beta3, ln_lambda1, ln_lambda2):
        lambda1 = np.exp(ln_lambda1)   # ensure positivity
        lambda2 = np.exp(ln_lambda2)

        L1 = _load_ns_component(maturity, lambda1)
        L2 = L1 - np.exp(-maturity / lambda1)
        L3 = _load_ns_component(maturity, lambda2) - np.exp(-maturity / lambda2)

        return beta0 + beta1 * L1 + beta2 * L2 + beta3 * L3

    # Good initial values (widely used)
    p0 = [zero_rates[-1],      # beta0 ~ long rate
          -1.0,                # slope
          1.0,                 # curvature
          0.5,                 # 2nd curvature
          np.log(1.0),         # lambda1 ~ 1
          np.log(5.0)]         # lambda2 ~ 5

    # Parameter bounds (important to avoid nonsense)
    bounds = (
        [-5, -10, -10, -10, np.log(0.01), np.log(0.01)],  # lower
        [15, 10, 10, 10, np.log(30), np.log(30)]           # upper
    )

    params, _ = curve_fit(
        svensson, maturities, zero_rates,
        p0=p0,
        bounds=bounds,
        maxfev=20000
    )

    # return interpolation function
    def interpolate_(target_maturities: np.array) -> np.array:
        target_maturities = np.asarray(target_maturities).astype(float)
        return svensson(target_maturities, *params)

    return interpolate_