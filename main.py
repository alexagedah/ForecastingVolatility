import indicators

import pandas as pd
from sklearn.metrics import r2_score

def GetDF(forecast_period):
	"""
	Returns a DataFrame containing OHLC data along with the forecast_period day future realised volatility
		Parameters:
			forecast_period (int) : The number of days you want to forecast volatility ahead for
		Returns:
			df (DataFrame) : A DataFrame containing OHLC data on df along with the x day future realised volatility
	"""
	df = pd.read_csv("^IXIC.csv", index_col = 0, parse_dates = True)
	df.drop(columns = ["Adj Close","Volume"], inplace = True)
	indicators.AddHistoricalVolatility(df, forecast_period)
	df.loc[:,f"{forecast_period} Day Future Volatility"] = df.loc[:,"Historical Volatility"].shift(-forecast_period)
	df.drop(columns = ["Historical Volatility"], inplace = True)
	return df

def GetForecastDF(forecast_period):
	"""
	Returns a DataFrame which includes future realised volatility and various forecasts of it
		Parameters:
			forecast_period (int) : The number of days you want to forecast volatility ahead for
		Returns
			forecast_df (DataFrame) : A DataFrame containing the forecast_period day future realised volatility and various
			forecasts of it
	"""
	df = GetDF(forecast_period)
	indicators.AddHistoricalVolatility(df, forecast_period)
	indicators.AddCloseToCloseVolatility(df, forecast_period)
	indicators.AddParkinsonVolatility(df, forecast_period)
	indicators.AddGarmanKlassVolatility(df, forecast_period)
	indicators.AddRogersSatchellVolatility(df, forecast_period)
	df.dropna(inplace = True)
	forecast_df = df.drop(columns = ["Open","High","Low","Close"])
	return forecast_df

def EvaluateForecasts(forecast_period):
	"""
	Returns a DataFrame showing how well the various forecast methods perform for a specific forecast period
		Parameters:
			forecast_period (int) : The number of days you want to forecast volatility ahead for
		Returns:
			results_df (DataFrame) : DataFrame containing the results of the forecasts for a specific forecast period
	"""
	forecast_df = GetForecastDF(forecast_period)
	# print(forecast_df)
	future_vol = forecast_df.iloc[:,0]

	forecast_names = forecast_df.columns.values[1:]

	data = []

	for i, forecast_method in enumerate(forecast_names):
		forecast_vol = forecast_df.iloc[:,i+1]
		r2 = r2_score(future_vol,forecast_vol)
		df = pd.DataFrame({forecast_method:r2}, index = [forecast_period])
		data.append(df)
	results_df = pd.concat(data, axis = 1)
	return results_df

def ForecastPeriodLoop():
	"""
	Returns a DataFrame showing how well the various forecast methods perform for a range of forecast periods
		Returns:
			full_results_df (DataFrame) : A DataFrame containing the results of the forecasts for each forecast period
	"""
	data = []
	for i in range(5,250,5):
		print(i)
		results_df = EvaluateForecasts(i)
		data.append(results_df)
	full_results_df = pd.concat(data, axis = 0)
	return full_results_df

full_results_df = ForecastPeriodLoop()

writer = pd.ExcelWriter("Results.xlsx")
full_results_df.to_excel(writer,"Sheet 1")
writer.save()
