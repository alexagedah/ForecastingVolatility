# Forecasting Volatility
Forecasting volatility is key to trading volatility succesfully. If an option trader can forecast volatility more accurately than the market, they can profit from the difference between realised volatility and implied volatility. The aim of this project was to compare the performance of different methods used to forecast volatility. The two methods explored were the GARCH(1,1) model and rolling window method. In the rolling window method, the estimators used to estimate true volatility were 
- historical volatility
- close-to-close volatility
- Parkinson volatility
- Garman-Klass volatility
- Rogers-Satchell volatility
The forecasts were done on the Nasdaq composite however this can easily be changed to any other asset class.

# Method, Results and Discussion
The R squared statistic was used to measure the performance of the methods. They produced predicted values of  future realised volatility over the next x days these were compared with the actual value of future realised volatility over the next x days. Below are the results showing the R squared statistics for when the rolling window method was used with different estimators.

<img width="622" alt="Screenshot 2022-09-30 at 03 03 17" src="https://user-images.githubusercontent.com/108612856/193174305-62cd9093-eaeb-4882-88c7-208d6c3403b8.png">

The rolling window method performed best when forecasting volatility over the next 10 days. For more days than this, performance declined and was particularly poor when using periods over 100 days. This is likely because when there is a large move in the asset, this moves remains in the forecast for x days and then suddenly drops out. Equity indices often experience spikes in volatility which then decay with time and so the rolling window method would perform badly for x days after a large spike in volatility.

The GARCH(1,1) model was used to forecast volatility over the next 20 days. The NASDAQ data was split into a training set to estimate the parameters for the model using the MLE method, and then tested on a training set. The scipy.optimise module was used to maximise the likelihood function. The R squared for the GARCH(1,1) R squared was -1.5! This is a very bad R squared and there are various possible reasons for it
- A bug in the code (I need to go through my code and make sure there are no errors)
- The scipy.optimise module is not estimating the MLE parameters. The parameters it gave were quite different from the parameters from the Hull book example so the optimisation procedure needs to be investigated
- Poor model. The GARCH(1,1) model may be a poor model (look into research on the model and see what other results are)
- Non-optimal forecast period. I only tested the model forecasting volatility over the next 20 days. Is there a better period that the GARCH model works for? If so, why is this true?

# Conclusion
This serves is a good introduction to forecasting volatility. The next steps are to tweak the code to make a full framework which can be used to assess methods for forecasting volatility, save the results and make comparisons to other methods.
