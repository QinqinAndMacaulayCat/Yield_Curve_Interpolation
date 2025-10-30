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

    f_intervals = -(np.diff(np.log(dfs)) / np.diff(maturities))

    f_nodes = np.r_[f_intervals[0], (f_intervals[:-1] + f_intervals[1:]) / 2, f_intervals[-1]]
    
    def interpolate_(target_maturities: np.array) -> np.array:
        estimated_dfs = CubicHermiteSpline(target_maturities)
        estimated_yields = -np.log(estimated_dfs) / target_maturities
        return estimated_yields

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

    def nelson_siegel(maturity, beta0, beta1, beta2, lambda_):
        term1 = beta0
        term2 = beta1 * ((1 - np.exp(-maturity / lambda_)) / (maturity / lambda_))
        term3 = beta2 * (((1 - np.exp(-maturity / lambda_)) / (maturity / lambda_)) - np.exp(-maturity / lambda_))
        return term1 + term2 + term3
    
    params, _ = curve_fit(nelson_siegel, maturities, zero_rates, maxfev=10000)

    def interpolate_(target_maturities: np.array) -> np.array:
        return nelson_siegel(target_maturities, *params)

    return interpolate_

def Svensson_interpolation(zero_rates: np.array,
                            maturities: np.array) -> callable:
    """
    Perform Svensson interpolation on the given zero rates to estimate yields at target maturities.
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
    def svensson(maturity, beta0, beta1, beta2, beta3, lambda1, lambda2):
        term1 = beta0
        term2 = beta1 * ((1 - np.exp(-maturity / lambda1)) / (maturity / lambda1))
        term3 = beta2 * (((1 - np.exp(-maturity / lambda1)) / (maturity / lambda1)) - np.exp(-maturity / lambda1))
        term4 = beta3 * (((1 - np.exp(-maturity / lambda2)) / (maturity / lambda2)) - np.exp(-maturity / lambda2))
        return term1 + term2 + term3 + term4
    params, _ = curve_fit(svensson, maturities, zero_rates, maxfev=10000)

    def interpolate_(target_maturities: np.array) -> np.array:
        return svensson(target_maturities, *params)

    return interpolate_