

# Introduction

Yield curve construction is a fundamental task in finance, particularly in the valuation of fixed-income securities. A yield curve represents the relationship between interest rates (or yields) and different maturities. In practice, only a limited number of market instruments are available to derive the yield curve, necessitating the use of interpolation methods to estimate yields for maturities not directly observed in the market. 

The preferable properties of interpolation methods for yield curve construction include:

| Property | Description | Why Important for Yield Curve Construction |
|----------|-------------|--------------------------------------------|
|No-arbitrage| Forward rates are non-negative | Ensures that the constructed yield curve does not imply arbitrage opportunities, which is crucial for accurate pricing of financial instruments. |
|Exactness| Reproduces market prices | Ensures that the yield curve accurately reflects the prices of the underlying market instruments, leading to reliable valuations. |
|Locality| Changes in one part of the curve do not affect distant parts | Allows for adjustments to specific segments of the yield curve without unintended consequences on other segments, enhancing flexibility in curve construction. |
|Stability| Small changes in input data lead to small changes in output | Ensures that the yield curve is robust to minor fluctuations in market data, providing confidence in the derived yields. |
|Local Hedging| Enables hedging of instruments using nearby maturities | Facilitates effective risk management by allowing traders to hedge positions using instruments with similar maturities, reducing basis risk.|

Some common interpolation methods used in yield curve construction include:

| Method | Description | Space |
|--------|-------------|----------------|
|Linear Interpolation| Connects data points with straight lines | 


# Polynomial Spline

A polynomial spline is a piecewise-defined polynomial function that maintains a high degree of smoothness at the points where the polynomial pieces connect, known as knots. Splines are widely used in numerical analysis, computer graphics, and data interpolation due to their flexibility and ability to approximate complex shapes.

## Cubic Spline
A cubic spline is a specific type of polynomial spline where each piece is a third-degree polynomial. Cubic splines are particularly popular because they provide a good balance between flexibility and smoothness.

Properties of cubic splines include:
- Continuity: The spline is continuous across the entire interval.
- Smoothness: The first and second derivatives of the spline are continuous at the knots.

Drawbacks:
- Runge's Phenomenon: High-degree polynomials can exhibit oscillatory behavior, especially near the edges of the interval.

Formulation:
Given a set of data points $(x_0, y_0), (x_1, y_1), \ldots, (x_n, y_n)$, a cubic spline $S(x)$ is defined piecewise as:

$$
S_i(x) = a_i + b_i(x - x_i) + c_i(x - x_i)^2 + d_i(x - x_i)^3, \quad x \in [x_i, x_{i+1}]
$$

where $S_i(x)$ is the cubic polynomial for the interval $[x_i, x_{i+1}]$ and $a_i, b_i, c_i, d_i$ are coefficients determined by the conditions of continuity and smoothness at the knots.
To determine the coefficients, we set up a system of equations based on the following conditions:

$$
\begin{align*}
S_i(x_i) &= y_i \quad \text{(interpolation condition)} \\
S_i(x_{i+1}) &= y_{i+1} \quad \text{(interpolation condition)} \\
S_i'(x_{i+1}) &= S_{i+1}'(x_{i+1}) \quad \text{(first derivative continuity)} \\
S_i''(x_{i+1}) &= S_{i+1}''(x_{i+1}) \quad \text{(second derivative continuity)}
\end{align*}
$$

Boundary Conditions:
- Natural Spline: The second derivative at the endpoints is set to zero.
- Clamped Spline: The first derivative at the endpoints is specified.
- Not-a-Knot Spline: The third derivative is continuous at the second and penultimate knots.
- Periodic Spline: The function and its first and second derivatives are equal at the endpoints.


## n th Degree Spline

An n th degree spline is a piecewise polynomial function where each piece is a polynomial of degree n. The properties of n th degree splines include:

- Continuity: The spline is continuous across the entire interval.
- Smoothness: The first (n-1) derivatives of the spline are continuous at the knots.

Formulation:
Given a set of data points $(x_0, y_0), (x_1, y_1), \ldots, (x_n, y_n)$, an n th degree spline $S(x)$ is defined piecewise as:

$$
S_i(x) = a^0_i + a^1_i(x - x_i) + a^2_i(x - x_i)^2 + \ldots + a^n_i(x - x_i)^n, \quad x \in [x_i, x_{i+1}]
$$

where $S_i(x)$ is the n th degree polynomial for the interval $[x_i, x_{i+1}]$ and $a^0_i, a^1_i, \ldots, a^n_i$ are coefficients determined by the conditions of continuity and smoothness at the knots.

To determine the coefficients, we set up a system of equations based on the following conditions:

$$
\begin{align*}
S_i(x_i) &= y_i \quad \text{(interpolation condition)} \\
S_i(x_{i+1}) &= y_{i+1} \quad \text{(interpolation condition)} \\
S_i^{(k)}(x_{i+1}) &= S_{i+1}^{(k)}(x_{i+1}) \quad \text{for } k = 1, 2, \ldots, n-1 \quad \text{(derivative continuity)}
\end{align*}
$$



