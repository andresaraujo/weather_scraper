from flask import Flask, jsonify 
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)


# Cookies and Session (Could be moved outside the endpoint for efficiency)
cookies = {'unitOfMeasurement': 'm'}
session = requests.Session()


# @app.route('/weather/<latitude>/<longitude>', methods=['GET'])
@app.route('/weather/<latitude>/<longitude>', methods=['GET'])
def get_weather(latitude, longitude):
    url = f"https://weather.com/weather/today/l/{latitude},{longitude}?par=google" 

    try:
        response = session.get(url, cookies=cookies)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        # Remove scripts and SVGs (Not strictly necessary for data extraction)
        for script in soup("script"):
            script.decompose()
        for svg in soup.find('div', id="todayDetails")("svg"):
            svg.decompose()

        # Extract and organize data as before
        data = {}
        main_element = soup.find('div', id="todayDetails")
        air_quality_element = soup.find('div', {'data-testid': 'AirQualityCard'}) 
        weather_items = main_element.find_all('div', {'data-testid': 'WeatherDetailsListItem'})


        feels_like = main_element.find('span', {'data-testid': 'TemperatureValue'})
        data["feels_like"] = feels_like.text

        sunset = main_element.find('div', {'data-testid': 'SunsetValue'})
        data["sunset"] = sunset.text

        sunrise = main_element.find('div', {'data-testid': 'SunriseValue'})
        data["sunrise"] = sunrise.text

        for item in weather_items:
            label = item.find('div', {'data-testid': 'WeatherDetailsLabel'}).text.strip()
            value_elem = item.find('div', {'data-testid': 'wxData'})

            value = value_elem.text.strip() if value_elem else "N/A"  # Handle case if value not found

            # replace non-breaking spaces with regular spaces
            value = value.replace('\xa0', ' ')


            if label == "High / Low":
                high, low = value.split('/')
                data["high"] = high
                data["low"] = low
            else:
                data[label.lower().replace(" ", "_")] = value

        air_quality = air_quality_element.find('text', {'data-testid': 'DonutChartValue'})
        data["air_quality"] = air_quality.text

        air_quality_severity = air_quality_element.find('p', {'data-testid': 'AirQualitySeverity'})
        data["air_quality_severity"] = air_quality_severity.text

        air_quality_category = air_quality_element.find('span', {'data-testid': 'AirQualityCategory'})
        data["air_quality_category"] = air_quality_category.text

        return jsonify(data) 
    except requests.exceptions.RequestException as e:
        return jsonify({"error": "Failed to fetch weather data"}), 500

if __name__ == '__main__':
    from werkzeug.middleware.proxy_fix import ProxyFix
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_host=1) 
    app.run(debug=True)
