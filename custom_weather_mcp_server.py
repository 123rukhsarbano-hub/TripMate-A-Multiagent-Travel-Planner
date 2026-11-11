from mcp.server.fastmcp import FastMCP
import requests
import os 
from dotenv import load_dotenv
load_dotenv()

import logging
logging.basicConfig(level=logging.INFO)

mcp=FastMCP("Weather MCP Server")
OPENWEATHER_API_KEY=os.getenv("OPENWEATHER_API_KEY")

@mcp.tool()
def get_current_weather(city: str):
    try:
        response = requests.get("https://api.openweathermap.org/data/2.5/weather",
                    params={
                        "q": city,
                        "appid": OPENWEATHER_API_KEY,
                        "units": "metric"
                    })
        data = response.json()
        
        # if response.status_code != 200:
        #     return data
    except Exception as e:
        import traceback
        print(f"Could not connect to custom weather MCP")

        traceback.print_exception(
            type(e),
            e,
            e.__traceback__
        )
    
    return{
        "city": data["name"],
        "temperature_c": data["main"]["temp"],
        "feels_like_c": data["main"]["feels_like"],
        "humidity": data["main"]["humidity"],
        "condition": data["weather"][0]["description"],
        "wind_speed": data["wind"]["speed"]
    }

@mcp.tool()
def get_weather_forecast(city: str):
    url = ("https://api.openweathermap.org/data/2.5/forecast")
    params = {
        "q": city,
        "appid": OPENWEATHER_API_KEY,
        "units": "metric"
    }
    response = requests.get(url, params=params)
    data = response.json()
    
    if response.status_code != 200:
        return data
    
    # return first 5 forecast entries
    forecast = []
    
    for item in data["list"][:5]:
        forecast.append(
            {
                "datetime": item["dt_txt"],
                "temperature": item["main"]["temp"],
                 "weather": item["weather"][0]["description"]
            }
        )
        
    return {
        "city": city,
        "forecast": forecast
    }
    
if __name__ == "__main__":
    mcp.run()