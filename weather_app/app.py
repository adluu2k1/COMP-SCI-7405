import os
from flask import Flask, render_template, request
import requests
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()
API_KEY = os.getenv("API_KEY")
BASE_URL = "https://api.openweathermap.org/data/2.5/"

app = Flask(__name__)

def kelvin_to_celsius(kelvin):
    return round(kelvin - 273.15, 1)

@app.route("/", methods=["GET", "POST"])
def index():
    weather_data = None
    forecast_data = None
    location = "Hanoi"

    if request.method == "POST":
        location = request.form.get("location")

    # Current weather
    current_url = f"{BASE_URL}weather?q={location}&appid={API_KEY}"
    current_response = requests.get(current_url).json()

    if current_response.get("cod") != 200:
        error_message = current_response.get("message", "Location not found.")
        return render_template("index.html", error=error_message)

    weather_data = {
        "city": current_response["name"],
        "temperature": kelvin_to_celsius(current_response["main"]["temp"]),
        "description": current_response["weather"][0]["description"].capitalize(),
        "humidity": current_response["main"]["humidity"],
        "wind_speed": current_response["wind"]["speed"],
        "icon": current_response["weather"][0]["icon"],
    }

    # Forecast (5-hour & 3-day)
    forecast_url = f"{BASE_URL}forecast?q={location}&appid={API_KEY}"
    forecast_response = requests.get(forecast_url).json()

    if forecast_response.get("cod") != "200":
        forecast_data = None
    else:
        # Next 5 hours (next 5 3-hour intervals)
        next_5_hours = forecast_response["list"][:5]
        next_5_hours_data = []
        for item in next_5_hours:
            next_5_hours_data.append({
                "time": datetime.fromtimestamp(item["dt"]).strftime("%H:%M"),
                "temp": kelvin_to_celsius(item["main"]["temp"]),
                "description": item["weather"][0]["description"].capitalize(),
                "icon": item["weather"][0]["icon"],
            })

        # Next 3 days (grouped by day)
        days = {}
        for item in forecast_response["list"]:
            date_str = datetime.fromtimestamp(item["dt"]).strftime("%Y-%m-%d")
            if date_str not in days:
                days[date_str] = []
            days[date_str].append(item)

        next_3_days_data = []
        dates = list(days.keys())[:3]
        for date in dates:
            day_data = days[date][0]  # pick first forecast of the day
            next_3_days_data.append({
                "date": date,
                "temp": kelvin_to_celsius(day_data["main"]["temp"]),
                "description": day_data["weather"][0]["description"].capitalize(),
                "icon": day_data["weather"][0]["icon"],
            })

        forecast_data = {
            "next_5_hours": next_5_hours_data,
            "next_3_days": next_3_days_data
        }

    return render_template("index.html", weather=weather_data, forecast=forecast_data, location=location)

if __name__ == "__main__":
    app.run(debug=True)
