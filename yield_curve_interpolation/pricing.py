"""
Module for pricing bonds

Includes:
- Function to price a bond given cash flows, maturities, and zero rates.
- Bond class with methods to calculate price, clean price, and accrued interest.

"""
import numpy as np
import datetime
from scipy.optimize import minimize
from .utils import spot_to_discount


def price_bond(cash_flows: np.array,
               maturities: np.array,
               zero_rates: np.array,
               compounding_freq: int = 1,
               continuous: bool = False) -> float:
    """
    Price a bond given its cash flows, maturities, and zero rates.

    Parameters
    ----------
    cash_flows : np.array
        Array of cash flows of the bond.
    maturities : np.array
        Array of maturities corresponding to the cash flows.
    zero_rates : np.array
        Array of zero rates corresponding to the maturities.
    compounding_freq : int, optional
        Compounding frequency per year. Default is 1 (annual compounding).
    continuous : bool, optional
        Whether the rates are continuously compounded. Default is False.

    Returns
    -------
    float
        The price of the bond.
    """
    discount_data = spot_to_discount(zero_rates, maturities, compounding_freq, continuous)
    discount_factors = discount_data[1]

    bond_price = sum(cf * df for cf, df in zip(cash_flows, discount_factors))
    return bond_price



class bond:
    def __init__(self, 
                 id: str,
                 face_value: float,
                 coupon_rate: float,
                 first_coupon_date: datetime.date,
                 maturity_date: datetime.date,
                 payment_freq: int = 1, 
                 today: datetime.date = datetime.date.today()):
        
        self.id = id
        self.face_value = face_value
        self.coupon_rate = coupon_rate
        self.payment_freq = payment_freq
        self.first_coupon_date = first_coupon_date
        self.maturity_date = maturity_date
        self.today = today

        self.__all_payment_dates = self.get_all_payment_dates()
        self.__all_cash_flows = self.get_all_cash_flows()

    
    def set_today(self, new_today: datetime.date) -> None:
        """Set a new 'today' date for the bond."""
        self.today = new_today
    
    def get_all_cash_flows(self) -> np.array:
        """Generate cash flows for the bond."""
        if self.payment_freq <= 0:
            cash_flows = np.array([self.face_value + self.face_value * self.coupon_rate])
        else:
            cash_flows = np.full(len(self.__all_payment_dates), self.face_value * self.coupon_rate / self.payment_freq)
            cash_flows[-1] += self.face_value
        return cash_flows

    def get_all_payment_dates(self, ) -> list:
        """Generate payment dates for the bond."""
        if self.payment_freq <= 0:
            return [self.maturity_date]
        payment_dates = []
        current_date = self.first_coupon_date
        while current_date < self.maturity_date:
            payment_dates.append(current_date)
            month = current_date.month + 12 // self.payment_freq
            year = current_date.year + (month - 1) // 12
            month = (month - 1) % 12 + 1
            day = min(current_date.day, (datetime.date(year + (month // 12), (month % 12) + 1, 1) - datetime.timedelta(days=1)).day)
            current_date = datetime.date(year, month, day)
        payment_dates.append(self.maturity_date)
        return payment_dates
    
    @property
    def maturity(self) -> float:
        """Calculate the maturity in years from today."""
        return (self.maturity_date - self.today).days / 365.25

    @property
    def maturities(self) -> np.array:
        """Generate year fractions for the bond's payment dates from today."""
        payment_dates = self.__all_payment_dates
        maturities = np.array([(date - self.today).days / 365.25 for date in payment_dates])
        maturities = maturities[maturities > 0]
        return maturities

    @property
    def cash_flows(self) -> np.array:
        """Get cash flows corresponding to future payment dates."""
        len_ = len(self.maturities)
        return self.__all_cash_flows[-len_:]


    def calc_price(self,
              zero_rates: np.array,
              compounding_freq: int = 1,
              continuous: bool = False) -> float:
        """
        Price the bond using the provided zero rate generator.

        Parameters
        ----------
        zero_rates : np.array
            Array of zero rates corresponding to the maturities.
        compounding_freq : int, optional
            Compounding frequency per year. Default is 1 (annual compounding).
        continuous : bool, optional
            Whether the rates are continuously compounded. Default is False.

        Returns
        -------
        float
            The price of the bond.
        """
        return price_bond(self.cash_flows,
                          self.maturities,
                          zero_rates,
                          compounding_freq,
                          continuous)

    def accrued_interest(self) -> float:
        """Calculate the accrued interest of the bond."""
        last_coupon_date = max(date for date in self.__all_payment_dates if date <= self.today)
        next_coupon_date = min(date for date in self.__all_payment_dates if date > self.today)

        days_since_last_coupon = (self.today - last_coupon_date).days
        days_between_coupons = (next_coupon_date - last_coupon_date).days

        accrued_interest = (self.face_value * self.coupon_rate / self.payment_freq) * (days_since_last_coupon / days_between_coupons)
        return accrued_interest

    def calc_clean_price(self,
                         zero_rates: np.array,
                         compounding_freq: int = 1,
                         continuous: bool = False) -> float:
        """
        Calculate the clean price of the bond.

        Parameters
        ----------
        zero_rates : np.array
            Array of zero rates corresponding to the maturities.
        compounding_freq : int, optional
            Compounding frequency per year. Default is 1 (annual compounding).
        continuous : bool, optional
            Whether the rates are continuously compounded. Default is False.

        Returns
        -------
        float
            The clean price of the bond.
        """
        dirty_price = self.calc_price(zero_rates, compounding_freq, continuous)
        accrued_interest = self.accrued_interest()
        clean_price = dirty_price - accrued_interest
        return clean_price

    def calc_ytm(self, 
                 market_price: float,
                 continuous: bool = False,
                 compounding_freq: int = 1,
                 guess: float = 0.05,
                 tol: float = 1e-6,
                 max_iter: int = 100) -> float:
        """
        Calculate the yield to maturity (YTM) of the bond using the Newton-Raphson method.

        Parameters
        ----------
        market_price : float
            The market price of the bond.
        guess : float, optional
            Initial guess for the YTM. Default is 0.05 (5%).
        tol : float, optional
            Tolerance for convergence. Default is 1e-6.
        max_iter : int, optional
            Maximum number of iterations. Default is 100.

        Returns
        -------
        float
            The yield to maturity of the bond.
        """
        
        def f(ytm):
            zero_rates = np.full(len(self.maturities), ytm)
            return (self.calc_price(zero_rates, continuous=continuous, compounding_freq=compounding_freq) - market_price) ** 2
        

        result = minimize(f, guess, tol=tol, options={'maxiter': max_iter})
        if result.success:
            return result.x[0]
        else:
            print("YTM calculation did not converge.")
            return float('nan')




