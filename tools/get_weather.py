import openmeteo_requests
import pandas as pd
from smolagents import tool

@tool
def get_weather_forecast(latitude: float, longitude: float) -> pd.DataFrame:
	"""
	Fetches the weather forecast for the 24 hours of current day using Open Meteo API.
	Args:
		latitude (float): Latitude of the location.
		longitude (float): Longitude of the location.
	Returns:
		pd.DataFrame: A DataFrame containing the hourly weather forecast with columns:
			- hour: Hour of the day (0-23).
			- temperature_2m: Temperature in degrees Celsius.
			- precipitation: Precipitation in mm.
	"""
	# Initialize the Open Meteo API client.
	openmeteo = openmeteo_requests.Client()
	url = "https://previous-runs-api.open-meteo.com/v1/forecast"

	try:
		params = {
			"latitude": latitude,
			"longitude": longitude,
			"hourly": ["temperature_2m", "precipitation"],
			"past_days": 0,
			"forecast_days": 1
		}
		responses = openmeteo.weather_api(url, params=params)
		response = responses[0]
	except Exception as e:
		return None

	# Process hourly data.
	hourly = response.Hourly()
	hourly_temperature_2m = hourly.Variables(0).ValuesAsNumpy()
	hourly_rain = hourly.Variables(1).ValuesAsNumpy()

	hourly_data = {"date": pd.date_range(
		start = pd.to_datetime(hourly.Time(), unit = "s", utc = True),
		end = pd.to_datetime(hourly.TimeEnd(), unit = "s", utc = True),
		freq = pd.Timedelta(seconds = hourly.Interval()),
		inclusive = "left"
	)}

	# Create a DataFrame with the hourly data.
	hourly_data["temperature_2m"] = hourly_temperature_2m
	hourly_data["precipitation"] = hourly_rain
	hourly_dataframe = pd.DataFrame(data = hourly_data)
	hourly_dataframe["hour"] = hourly_dataframe["date"].dt.hour

	# Convert the DataFrame to a dictionary.
	weather_forecast = hourly_dataframe[["hour", "temperature_2m", "precipitation"]]

	return weather_forecast