```
User:
----
Generate code to build a Weather Forecast website in Python that meet the following requirements. Instruct me how to run this application.
Requirements:
- Source: Find and choose a weather source and include it in the app.
- Should have a nice look and feel.
- Include temperature, weather state (cloudy, sunny, rainy,...), wind speed, humidity.
- Allow to choose location.
- Show predicted weather in the next 5 hours and next 3 days if available.
```

Got it! Let’s create a Python web application that meets your requirements:

✅ Use a **popular weather API** (like OpenWeatherMap)
✅ Use **Flask** for a simple web framework
✅ Use **Bootstrap** for a clean, responsive look
✅ Show **current weather**, **next 5 hours** (if available), and **next 3 days**

---

### 📦 Step 1: Install Required Packages

Make sure you have Python (3.7+) installed. Then run:

```bash
pip install flask requests python-dotenv
```

---

### ⚙️ Step 2: Obtain API Key

1. Create a free account at **OpenWeatherMap**: [https://openweathermap.org/api](https://openweathermap.org/api)
2. Get your **API Key** (a string like `abcd1234abcd1234abcd1234`).

---

### 📁 Step 3: Create Project Structure

```
weather_app/
├── app.py
├── .env
├── templates/
│   └── index.html
├── static/
│   └── style.css
└── requirements.txt
```

---

### ✏️ Step 4: Create `.env` File

In the root of `weather_app/`, create `.env`:

```plaintext
API_KEY=your_api_key_here
```

Replace `your_api_key_here` with your OpenWeatherMap API key.

---

### 🖥️ Step 5: Create `app.py`

```python
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
```

---

### 🖼️ Step 6: Create `templates/index.html`

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Weather Forecast</title>
    <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css">
    <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">
</head>
<body class="bg-light">
    <div class="container py-4">
        <h1 class="text-center mb-4">🌤️ Weather Forecast</h1>
        <form method="post" class="form-inline justify-content-center mb-4">
            <input type="text" name="location" class="form-control mr-2" placeholder="Enter location" value="{{ location }}">
            <button type="submit" class="btn btn-primary">Get Weather</button>
        </form>

        {% if error %}
            <div class="alert alert-danger">{{ error }}</div>
        {% endif %}

        {% if weather %}
            <div class="card mb-4">
                <div class="card-body text-center">
                    <h2>{{ weather.city }}</h2>
                    <img src="http://openweathermap.org/img/wn/{{ weather.icon }}@2x.png" alt="icon">
                    <p>{{ weather.description }}</p>
                    <p><strong>Temperature:</strong> {{ weather.temperature }}°C</p>
                    <p><strong>Humidity:</strong> {{ weather.humidity }}%</p>
                    <p><strong>Wind Speed:</strong> {{ weather.wind_speed }} m/s</p>
                </div>
            </div>

            <h3>Next 5 Hours</h3>
            <div class="d-flex overflow-auto mb-4">
                {% for hour in forecast.next_5_hours %}
                    <div class="card mx-2 text-center p-2">
                        <p><strong>{{ hour.time }}</strong></p>
                        <img src="http://openweathermap.org/img/wn/{{ hour.icon }}@2x.png" alt="icon">
                        <p>{{ hour.description }}</p>
                        <p>{{ hour.temp }}°C</p>
                    </div>
                {% endfor %}
            </div>

            <h3>Next 3 Days</h3>
            <div class="d-flex justify-content-around">
                {% for day in forecast.next_3_days %}
                    <div class="card text-center p-2">
                        <p><strong>{{ day.date }}</strong></p>
                        <img src="http://openweathermap.org/img/wn/{{ day.icon }}@2x.png" alt="icon">
                        <p>{{ day.description }}</p>
                        <p>{{ day.temp }}°C</p>
                    </div>
                {% endfor %}
            </div>
        {% endif %}
    </div>
</body>
</html>
```

---

### 🎨 Step 7: Create `static/style.css`

```css
body {
    font-family: Arial, sans-serif;
}

.card {
    min-width: 150px;
}

.card img {
    width: 60px;
}
```

---

### 📄 Step 8: Create `requirements.txt`

```
flask
requests
python-dotenv
```

---

### 🚀 Step 9: Run the Application

In the terminal:

```bash
export FLASK_APP=app.py
flask run
```

On Windows (PowerShell):

```bash
set FLASK_APP=app.py
flask run
```

Open your browser and go to **[http://127.0.0.1:5000/](http://127.0.0.1:5000/)**.

---

### ⚡ Summary

✅ **Clean UI** with Bootstrap
✅ **Current Weather** with icon
✅ **Next 5 hours forecast**
✅ **Next 3 days forecast**
✅ **Location search**

Let me know if you’d like to deploy this app (e.g., on Heroku or Render) or customize further!

