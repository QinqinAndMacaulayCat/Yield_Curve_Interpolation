"""

Utility functions for yield curve interpolation.

"""
from typing import Dict, List
import numpy as np

def spot_to_discount(zero_rates: np.array,
                     maturities: np.array,
                     compounding_freq: int = 1,
                     continuous: bool = False
                     ) -> Dict[int, np.array]:
    """
    Convert spot (zero) rates to discount factors.

    Parameters
    ----------
    zero_rates : np.array
        Array of zero rates.
    maturities : np.array
        Array of maturities corresponding to the zero rates.
    compounding_freq : int, optional
        Compounding frequency per year. Default is 1 (annual compounding).
    continuous : bool, optional
        Whether the rates are continuously compounded. Default is False.

    Returns
    -------
    dict
        Dictionary with keys 0 and 1, where key 0 is the maturities and key 1 is the discount factors.
    """
    if continuous:
        discount_factors = np.exp(-zero_rates * maturities)
    else:
        discount_factors = 1 / (1 + zero_rates / compounding_freq) ** (compounding_freq * maturities)
    return {0: maturities, 1: discount_factors}

def discount_to_spot(discount_factors: np.array,
                     maturities: np.array,
                     compounding_freq: int = 1,
                     continuous: bool = False
                     ) -> Dict[int, np.array]:
    """
    Convert discount factors to spot (zero) rates.

    Parameters
    ----------
    discount_factors : np.array
        Array of discount factors.
    maturities : np.array
        Array of maturities corresponding to the discount factors.
    compounding_freq : int, optional
        Compounding frequency per year. Default is 1 (annual compounding).
    continuous : bool, optional
        Whether to compute continuously compounded rates. Default is False.

    Returns
    -------
    dict
        Dictionary with keys 0 and 1, where key 0 is the maturities and key 1 is the zero rates.
    """
    if continuous:
        zero_rates = -np.log(discount_factors) / maturities
    else:
        zero_rates = compounding_freq * ((1 / discount_factors) ** (1 / (compounding_freq * maturities)) - 1)
    return {0: maturities, 1: zero_rates}

def transform_rates(rates: np.array,
                    from_freq: int,
                    to_freq: int) -> np.array:
    """
    Transform rates from one compounding frequency to another.
    Parameters
    ----------
    rates : np.array
        Array of rates to be transformed.
    from_freq : int
        Original compounding frequency.
    to_freq : int
        Target compounding frequency.
    """

    if from_freq == to_freq:
        return rates

    if from_freq == float('inf') or str(from_freq) == 'inf':
        df = np.exp(-rates)
    else:
        df = 1 / (1 + rates / from_freq) ** (from_freq)
    
    if to_freq == float('inf') or str(to_freq) == 'inf':
        transformed_rates = -np.log(df)
    else:
        transformed_rates = to_freq * (df ** (-1 / to_freq) - 1)
    return transformed_rates


def spot_to_fwd(zero_rates: np.array,
                maturities: np.array,
                compounding_freq: int = 1,
                continuous: bool = False
                ) -> Dict[int, np.array | List]:
    """
    Convert spot (zero) rates to forward rates.

    Parameters
    ----------
    zero_rates : np.array
        Array of zero rates.
    maturities : np.array
        Array of maturities corresponding to the zero rates.
    compounding_freq : int, optional
        Compounding frequency per year. Default is 1 (annual compounding).

    Returns
    -------

    """
    if continuous:
        forward_rates = (zero_rates[1:] * maturities[1:] - zero_rates[:-1] * maturities[:-1]) / (maturities[1:] - maturities[:-1])
        forward_rates = np.insert(forward_rates, 0, zero_rates[0])
    else:
        dfs = spot_to_discount(zero_rates, maturities, compounding_freq, continuous=False)[1]
        fwd_dfs = dfs[1:] / dfs[:-1]
        forward_rates = discount_to_spot(fwd_dfs, maturities[1:] - maturities[:-1], compounding_freq, continuous=False)[1]
        forward_rates = np.insert(forward_rates, 0, zero_rates[0])
    
    mat_ranges = [(0, maturities[0])] + [(maturities[i-1], maturities[i]) for i in range(1, len(maturities))]
    return {0: mat_ranges, 1: forward_rates}


def discount_to_fwd(discount_factors: np.array,
                    maturities: np.array,
                    compounding_freq: int = 1,
                    continuous: bool = False
                    ) -> Dict[int, np.array | List]:
    """
    Convert discount factors to forward rates.

    Parameters
    ----------
    discount_factors : np.array
        Array of discount factors.
    maturities : np.array
        Array of maturities corresponding to the discount factors.
    compounding_freq : int, optional
        Compounding frequency per year. Default is 1 (annual compounding).

    Returns
    -------
    dict
        Dictionary with keys 0 and 1, where key 0 is the list of maturity ranges and key 1 is the forward rates.
    """
    zero_rates = discount_to_spot(discount_factors, maturities, compounding_freq, continuous)[1]
    return spot_to_fwd(zero_rates, maturities, compounding_freq, continuous)

def fwd_to_discount(forward_rates: np.array,
                    mat_ranges: List[tuple],
                    compounding_freq: int = 1,
                    continuous: bool = False
                    ) -> Dict[int, np.array]:
    """
    Convert forward rates to discount factors.

    Parameters
    ----------
    forward_rates : np.array
        Array of forward rates.
    maturities : np.array
        Array of maturities corresponding to the forward rates.
    compounding_freq : int, optional
        Compounding frequency per year. Default is 1 (annual compounding).

    Returns
    -------
    dict
        Dictionary with keys 0 and 1, where key 0 is the maturities and key 1 is the discount factors.
    """

    mat_diffs = np.array([end - start for start, end in mat_ranges])
    dfs = spot_to_discount(forward_rates, mat_diffs, compounding_freq, continuous=continuous)[1]
    discount_factors = np.cumprod(dfs)
    maturities = np.array([end for _, end in mat_ranges])
    return {0: maturities, 1: discount_factors}


