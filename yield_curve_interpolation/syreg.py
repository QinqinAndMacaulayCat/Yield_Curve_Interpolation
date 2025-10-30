
from pysr import PySRRegressor
import numpy as np

def syreg_interpolation(dfs: np.array,
                        maturities: np.array,
                        domain: str = "df"
                        ) -> callable:
    """
    Perform symbolic regression interpolation on the given discount factors to estimate yields at target maturities.
    Parameters
    ----------
    dfs : np.array
        Discount factors or yields at known maturities.
    maturities : np.array
        Maturities corresponding to the yield curves.
    domain : str
        Domain of the input data, {"df" for discount factors, "yield" for yields, "log_df" for log discount factors}.
    Returns
    -------
    Callable
        Estimated yields at the target maturities.
    """


    X = maturities.reshape(-1, 1)

    if domain == "df":
        y = dfs
    elif domain == "yield":
        y = -np.log(dfs) / maturities
    elif domain == "log_df":
        y = -np.log(dfs)
    else:
        raise ValueError("Invalid domain. Choose from {'df', 'yield', 'log_df'}.")

    model = PySRRegressor(
        niterations=1000,
        binary_operators=["+", "-", "*", "/"],
        unary_operators=["exp", "log", "sin", "cos"],
        populations=10,
        population_size=100,
        maxsize=20,
        verbosity=0,
    )

    model.fit(X, y)

    def interpolate(target_maturities: np.array) -> np.array:
        estimated_RT = model.predict(target_maturities.reshape(-1, 1))
        estimated_yields = estimated_RT / target_maturities
        return estimated_yields

    return interpolate