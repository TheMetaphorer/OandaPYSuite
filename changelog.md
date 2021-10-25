### August 2021 ###

# 0.1.0 rev3 #
- Added documentation

# 0.1.0 rev2 # 
- Implemented addition feature on CandlesObject class. Renamed CandlesObject to CandleCluster for clarity
- Added ability to plot horizontal and vertical lines to `OANDAAPIObject.plot()`. To do so, run `plot(x=x1, style='vline')`. For a vertical line. For a horizontal line, use `'hline'` instead of `'vline'` and `y` instead of `x`.

### October 2021 ###

# 0.1.1 #

- Implemented Account objects. Account objects have every attribute present in `Account` per the OANDA REST API's documentation.
- Reimplemented `api.APIObject`'s `get_accounts()` method, this method can now be used to retrieve the account objects
of every account owned by the given Authorization token.
- Implemented a standard deviation indicator function `stats.std_indicator`. Period can be specified as with the `moving_average()`, indicator, default period is 10.