import math
import pandas as pd
import numpy as np

import scipy.optimize as optimize

import indicators

from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score

tdpy = 252 # Trading days per year)
def GetDF(forecast_period):
	"""
	Returns a DataFrame containing OHLC data along with the future realised volatility and log returns
		Parameters:
			forecast_period (int) : The number of days you want to forecast volatility ahead for
		Returns:
			df (DataFrame) : A DataFrame containing OHLC data on df along with the x day future realised volatility
	"""
	df = pd.read_csv("^IXIC.csv", index_col = 0, parse_dates = True)
	df.drop(columns = ["Adj Close","Volume"], inplace = True)
	close = df.loc[:,"Close"]
	df.loc[:,"Log Returns"] = np.log(close/close.shift(1))

	indicators.AddHistoricalVolatility(df, forecast_period)
	df.loc[:,"Future Volatility"] = df.loc[:,"Historical Volatility"].shift(-forecast_period)
	df.drop(columns = ["Historical Volatility"], inplace = True)
	df.dropna(inplace = True)
	return df

# def GARCH(omega, alpha, beta, log_returns):
# 	"""
# 	This function calculates the GARCH estimate of the current variance of single period log returns
# 		Parameters:
# 			omega (float)
# 			alpha (float)
# 			beta (float)
# 			log_returns (ndarray) : The log returns for the instrument
# 		Returns:
# 			garch_estimates (ndarray) : The estimates of the current variance of single period log returns
# 			log returns according to the GARCH(1,1) model
# 	"""
# 	prev_log_returns = log_returns[1:]
# 	garch_estimates = np.zeros(len(log_returns) - 1)
# 	# Initially set the Garch(1,1) forecast to the previous squared log returns
# 	garch_estimates[0] = prev_log_returns[0]**2
# 	for i in range(1,len(garch_estimates)):
# 		garch_estimates[i] = omega + alpha*prev_log_returns[i]**2 + beta*garch_estimates[i - 1]
# 	return garch_estimates

def GARCH(omega, alpha, beta, log_returns):
	"""
	This function calculates the GARCH estimate of the current variance of single period log returns
		Parameters:
			omega (float)
			alpha (float)
			beta (float)
			log_returns (Series) : The log returns for the instrument
		Returns:
			garch_estimates (Series) : The estimates of the current variance of single period log returns
			log returns according to the GARCH(1,1) model
	"""
	prev_log_returns = log_returns.shift(1)
	garch_estimates = pd.Series(0, index = log_returns.index)
	# Initially set the Garch(1,1) forecast to the previous squared log returns
	garch_estimates.iloc[0] = None
	garch_estimates.iloc[1] = prev_log_returns.iloc[1]**2
	for i in range(2,len(garch_estimates)):
		garch_estimates[i] = omega + alpha*prev_log_returns[i]**2 + beta*garch_estimates[i - 1]
	return garch_estimates

def GARCHVolatility(V_L_estimate, gamma, alpha, beta, T, log_returns):
	"""
	Calculates the GARCH estimate of the average variance of annual log returns
		Parameter:
			V_L_estimate (float)
			gamma (float)
			alpha (float)
			beta (float)
			T (int) : The number of days to forecast the variance over
		Returns:
			garch_vol (ndarray) : THe estimates of the volatility of the underlying over the
			next T periods
	"""
	V_0 = GARCH(V_L_estimate*gamma_estimate, alpha_estimate, beta_estimate, log_returns)
	a = math.log(1/(alpha + beta_estimate))
	garch_variance_estimate =tdpy*(V_L_estimate + (1 - math.exp(-a*T))*(V_0 - V_L_estimate))
	garch_vol = np.sqrt(garch_variance_estimate)
	return garch_vol

def LogLikelihood(garch_parameters, log_returns):
	"""
	Calculates minus the log likelihood of the data occuring
		Parameters:
			garch_parameters (list) : [omega, alpha, beta]
			log_returns (ndarray) : The log returns of the instrument
		Returns
			minus_log_likelihood (float) : Minus the log likelihood of the data occuring
	"""
	omega = garch_parameters[0]
	alpha = garch_parameters[1]
	beta = garch_parameters[2]

	garch_estimates = GARCH(omega, alpha, beta, log_returns)
	# The GARCH estimates can only start 1 period after the firstlog returns value 
	# so remove the 1st log returns value
	log_returns = log_returns[1:]

	minus_log_likelihood = - np.sum( -np.log(garch_estimates) - (log_returns**2)/garch_estimates)
	return minus_log_likelihood

def GARCHConstraint(garch_parameters):
	"""
	The contraint on the GARCH(1,1) model to ensure the process is mean reverting
		Parameters:
			garch_parameters (list) : [omega, alpha, beta]
	"""
	alpha = garch_parameters[1]
	beta = garch_parameters[2]
	return (1 - alpha - beta)

def FitGARCH(log_returns):
	"""
	Returns the parameters for the GARCH model
		Parameters:
			log_returns (ndarray) : The log returns for the instrument
		Return:
			V_L_estimate (float)
			gamma_estimate (float)
			alpha_estimate (float)
			beta_estimate (float)
	"""
	cons1 = ({'type': 'ineq', 'fun': lambda x: np.array(x)})
	cons2 = ({'type': 'ineq', 'fun': GARCHConstraint})
	cons = [cons1, cons2]
	# cons = {'type': 'ineq', 'fun': GARCHConstraint}

	initial_parameters = [0.1**4,0.01,0.9]
	result = optimize.minimize(fun = LogLikelihood,
		x0 = initial_parameters,
		args = log_returns,
		method = "SLSQP",
		bounds = ((0.1**7,0.1),(0.01,0.4),(0.7,0.99999)),
		constraints = cons,
		options = {"maxiter":1000,"disp":True}
	)
	omega_estimate = result.x[0]
	alpha_estimate = result.x[1]
	beta_estimate = result.x[2]
	gamma_estimate = 1 - alpha_estimate - beta_estimate
	V_L_estimate = omega_estimate/gamma_estimate

	print(f"Omega: {V_L_estimate}")
	print(f"Gamma: {gamma_estimate}")
	print(f"Alpha: {alpha_estimate}")
	print(f"Beta: {beta_estimate}")
	return V_L_estimate, gamma_estimate, alpha_estimate, beta_estimate

forecast_period = 20
df = GetDF(forecast_period)
X = df.loc[:,"Log Returns"]
y = df.loc[:,"Future Volatility"]

X_train, X_test, y_train, y_test = train_test_split(X,y,  test_size = 0.2, random_state = 42)
V_L_estimate, gamma_estimate, alpha_estimate, beta_estimate = FitGARCH(X_train)

forecast_train = GARCHVolatility(V_L_estimate, gamma_estimate, alpha_estimate, beta_estimate, forecast_period, X_train)

forecast_test = GARCHVolatility(V_L_estimate, gamma_estimate, alpha_estimate, beta_estimate, forecast_period, X_test)

train_r2 = r2_score(y_train.iloc[1:], forecast_train.iloc[1:])
test_r2 = r2_score(y_test.iloc[1:], forecast_test.iloc[1:])

print(f"Test R Squared {test_r2}")


