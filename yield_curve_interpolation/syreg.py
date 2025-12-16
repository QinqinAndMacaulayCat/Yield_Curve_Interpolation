
from pysr import PySRRegressor
import numpy as np
from .utils import discount_to_spot, discount_to_fwd, spot_to_discount, fwd_to_discount

def syreg_interpolation(inputs: np.array,
                        maturities: np.array,
                        domain: str = "df",
                        return_type: str = "yield"
                        ) -> callable:
    """
    Perform symbolic regression interpolation on the given discount factors to estimate yields at target maturities.
    Parameters
    ----------
    inputs : np.array
        Discount factors / yields / log discount factors at known maturities.
    maturities : np.array
        Maturities corresponding to the yield curves.
    domain : str
        Domain of the input data, {"df" for discount factors, "yield" for yields, "log_df" for log discount factors, "fwd" for forward rates}
    return_type : str
        Type of the output data, {"yield" for yields, "df" for discount factors, "log_df" for log discount factors, "fwd" for forward rates}
    Returns
    -------
    Callable
        Estimated yields/discount factors/log discount factors / fwd rates at the target maturities.
    """

    y = inputs
    X = maturities.reshape(-1, 1)

    model = PySRRegressor(
        niterations=1000,
        binary_operators=["+", "-", "*", "/"],
        unary_operators=["exp", "log", 'sqrt'],
        populations=10,
        population_size=100,
        maxsize=20,
        model_selection='best',
        verbosity=0,
    )

    model.fit(X, y)

    def interpolate(target_maturities: np.array) -> np.array:
        estimated = model.predict(target_maturities.reshape(-1, 1))
        
        if domain == "yield":
            estimated = spot_to_discount(estimated, target_maturities)[1]
        elif domain == "log_df":
            estimated = np.exp(-estimated)
        elif domain == "fwd":
            estimated = fwd_to_discount(estimated, target_maturities)[1]

        if return_type == "yield":
            results = discount_to_spot(estimated, target_maturities)[1]
        elif return_type == "df":
            results = estimated
        elif return_type == "log_df":
            results = -np.log(estimated)
        elif return_type == "fwd":
            results = discount_to_fwd(estimated, target_maturities)[1]
        else:
            raise ValueError("Invalid return_type.")

        return results

    return interpolate