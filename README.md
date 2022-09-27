# Forecasting Volatility 
Comparing the performance of historical volatility, close-to-close volatility, Parkinson volatility, Garman-Klass volatility and Rogers-Satchell volatility in the rolling window method to forecast future volatility on the Nasdaq composite.

Volatility exhibits serial correlation. Future volatility over some period of time is correlated to volatility over the previous period of time when both periods of time are the same. This is the basis on which the rolling window method for forecasting future volatility is built. Here the rolling window method is used to forecast future volatility and different estimators are used to estimate true volatility. Comparisons are then made in the performance of the different estimators. This is repeated for various forecast periods.

Going into this, I expect the close-to-close method to perform the best. Despite its low efficiency it is an unbiased estimator of true volatility whereas the Parkinson and Garmana-Klass estimators are biased. The Rogers-Satchell estimator is unbiased, however it performs badly when there are gaps. Future investigations on cryptocurrencies would be interesting as these rarely have gaps.
