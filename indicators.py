"""
This program contains all the indicators that are used to forecast future volatility
ALL THE FUNCTIONS ASSUME WE ARE GETTING END OF DAY DATA 
"""
tdpy = 252 # Trading days per year

import math
import scipy.special 
import pandas as pd
import numpy as np
 
def CloseToCloseVolatility(log_returns):
	"""
	This function calculates the close-to-close estimate of true volatility based on a Series containing the log returns
		Parameters:
			log_returns (Series) : A Series of log returns
		Returns:
			population_std_estimate (float) : An unbiased estimate for the (annualised) true volatility using the close-to-close estimator

	"""
	# Find the sample size we are using to estimate historical volatility
	N = log_returns.size
	# Calculate the sample variance setting the mean returns to 0
	sample_variance = (log_returns**2).sum() / N
	# Calculate the unbiased estimate for the population variance
	population_variance_estimate = N*sample_variance/(N - 1)
	# Calculate the biased estimate for the population standard deviation
	biased_population_std_estimate = math.sqrt(population_variance_estimate)
	b_N = math.sqrt(2/(N - 1)) * scipy.special.gamma(N/2)/scipy.special.gamma((N - 1)/2)
	population_std_estimate = math.sqrt(tdpy)*biased_population_std_estimate/b_N
	return population_std_estimate

def ParkinsonVolatility(log_high_low):
	"""
	Calculates the Parkinson estimate of true volatility based on a Series containing ln(high/low)
	Parameters:
			log_high_low (Series) : A Series of log(high/low)
		Returns:
			parkinson_estimate (float) : An estimate for the (annualised) true volatility using the Parkinson estimator
	"""
	term1 = (log_high_low**2).sum()
	N = log_high_low.size
	term2 = term1/(4*N*math.log(2))
	parkinson_estimate = math.sqrt(term2*tdpy)
	return parkinson_estimate

def GarmanKlassVolatilityTerm1(log_high_low):
	"""
	Calculates the 1st term in the Garman-Klass estimate of true volatility based on a Series containing ln(high/low)
	Parameters:
			log_high_low (Series) : A Series of log(high/low)
		Returns:
			term1 (float) : Term 1 in the Garman-Klass volatility equation
	"""
	N = log_high_low.size
	term1 = (log_high_low**2).sum()/(2*N)
	return term1

def GarmanKlassVolatilityTerm2(log_close_prev_close):
	"""
	Calculates the 2n  term in the Garman Klass estimate of true volatility based on a Series containing ln(high/low)
	Parameters:
			log_close_prev_close (Series) : A Series of log(close/prev_close)
		Returns:
			term2 (float) : Term 2 in the Garman-Klass volatility equation
	"""
	N = log_close_prev_close.size
	term2 = (2*math.log(2) - 1)*(log_close_prev_close**2).sum()/N
	return term2

def AddHistoricalVolatility(df, period):
	"""
	This function adds the standard deviation of log returns as a column to a OHLCV DataFrame over a period
		Parameters:
			df (DataFrame) : A Dataframe which contains the OHLCV time series data
			period (int) : The number of candles which we are calculating the standard deviation of log returns over.
	"""
	close = df.loc[:,"Close"]
	log_returns = np.log(close/close.shift(1))
	df.loc[:,"Historical Volatility"] = math.sqrt(tdpy)*log_returns.rolling(period).std()

def AddCloseToCloseVolatility(df, period):
	"""
	This function adds the annualised close-to-close volatility as a column to a DataFrame
	The DataFrame must have a column with closing prices
		Parameters:
			df (DataFrame) : A Dataframe which contains closing prices as a column
			period (int) : The number of candles which we estimating volatility over
	"""
	close = df.loc[:,"Close"]
	log_returns = np.log(close/close.shift(1))
	df.loc[:,"Close-to-close Volatility"] = log_returns.rolling(period).apply(CloseToCloseVolatility)

def AddParkinsonVolatility(df, period):
	"""
	Adds the annualised Parkinson volatility as a column to the DataFrame
	The DataFrame must have a column with the high and low price
		Parameters:
			df (DataFrame) : A Dataframe which contains closing prices as a column
			period (int) : The number of candles which we estimating volatility over
	"""
	high = df.loc[:,"High"]
	low = df.loc[:,"Low"]
	log_high_low = np.log(high/low)
	df.loc[:,"Parkinson Volatility"] = log_high_low.rolling(period).apply(ParkinsonVolatility)

def AddGarmanKlassVolatility(df, period):
	"""
	Adds the annualised Parkinson volatility as a column to the DataFrame
	The DataFrame must have a column with the high and low price
		Parameters:
			df (DataFrame) : A Dataframe which contains closing prices as a column
			period (int) : The number of candles which we estimating volatility over
	"""
	high = df.loc[:,"High"]
	low = df.loc[:,"Low"]
	close = df.loc[:,"Close"]
	prev_close = close.shift(1)
	log_high_low = np.log(high/low)
	log_close_prev_close = np.log(close/prev_close)

	term1 = log_high_low.rolling(period).apply(GarmanKlassVolatilityTerm1)
	term2 = log_close_prev_close.rolling(period).apply(GarmanKlassVolatilityTerm2)

	negative_gk_mask = (term2 > term1)
	df.loc[~negative_gk_mask,"Garman-Klass Volatility"] = np.sqrt(term1[~negative_gk_mask] - term2[~negative_gk_mask])*math.sqrt(tdpy)
	df.loc[negative_gk_mask,"Garman-Klass Volatility"] = 0

def AddRogersSatchellVolatility(df, period):
	"""
	Adds the annualised Parkinson volatility as a column to the DataFrame
	The DataFrame must have a column with the high and low price
		Parameters:
			df (DataFrame) : A Dataframe which contains closing prices as a column
			period (int) : The number of candles which we estimating volatility over
	"""
	o = df.loc[:,"Open"]
	h = df.loc[:,"High"]
	l = df.loc[:,"Low"]
	c = df.loc[:,"Close"]
	# Create a Series of the term used to calculate Rogers-Satchell volatility
	rogers_satchell_series = np.log(h/c)*np.log(h/o) + np.log(l/c)*np.log(l/o)

	sum_rs_series = np.sqrt(rogers_satchell_series.rolling(period).mean())
	df.loc[:,"Rogers-Satchell Volatility"] = sum_rs_series*math.sqrt(tdpy)

def AddYangZhangVolatility(df, sample_size):
	"""
	Adds the annualised Parkinson volatility as a column to the DataFrame
	The DataFrame must have a column with the high and low price
		Parameters:
			df (DataFrame) : A Dataframe which contains closing prices as a column
			sample_size (int) : The sample size to use in calculating close-to-close volatility
	"""
	pass




