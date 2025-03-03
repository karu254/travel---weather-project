import requests # Import requests library to make API requests
from flask import Flask, render_template, request # Import Flask, render_template and request classes
from datetime import datetime, timedelta # Import datetime and timedelta classes from datetime module

app = Flask(__name__) # Create a Flask app

UNSPLASH_ACCESS_KEY = 'dc6jtYZXUg2gbykw0ZNgUNmV0NMr8_KqMCW32t2tRA8' # Unsplash access key
UNSPLASH_API_URL = 'https://api.unsplash.com/search/photos' # Unsplash API URL

api_key = '7b4c337a7361cfa138e37b485821bb56'    # OpenWeatherMap API key


def get_day_of_week(date_str):   # Function to get the day of the week from a date string
    date_obj = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
    return date_obj.strftime("%A")  # Return the day of the week


def get_location_image(location_name):  # Function to get images related to a location
    headers = {
        'Authorization': f'Client-ID {UNSPLASH_ACCESS_KEY}' # Set the authorization header with the access key
    }
    params = {
        'query': location_name, # Search for the location name
        'per_page': 3  # Get three images
    }
    response = requests.get(UNSPLASH_API_URL, headers=headers, params=params) # Make a GET request to the Unsplash API
    data = response.json()
    if data.get('results'):
        return [photo['urls']['regular'] for photo in data['results']] # Return the URLs of the images
    else:
        return None


def weather_forecast(user_input): # Function to get the weather forecast for a location
    forecast_data = requests.get(
        f"https://api.openweathermap.org/data/2.5/forecast?q={user_input}&units=metric&appid={api_key}" # Make a GET request to the OpenWeatherMap API
    ).json()

    if forecast_data.get('cod') == '404': # Check if the city is not found
        return render_template("weather.html", error="City not found")
    else:
        city_name = forecast_data['city']['name']
        forecasts = {}
        today = datetime.now().date()
        end_date = today + timedelta(days=7)  # Get the date 7 days from today

        for forecast in forecast_data['list']:  # Loop through the forecast data
            date = forecast['dt_txt'].split()[0]  # Extracting date without time
            forecast_date = datetime.strptime(date, '%Y-%m-%d').date()
            if today <= forecast_date <= end_date: # Check if the forecast date is within the next 7 days
                day_of_week = get_day_of_week(forecast['dt_txt'])
                weather = forecast['weather'][0]['main']
                temp = round(forecast['main']['temp'])
                wind_speed = forecast['wind']['speed']  # Extract wind speed
                if date not in forecasts:  # Only add one forecast per day
                    forecasts[date] = {'date': date, 'day': day_of_week, 'weather': weather, 'temp': temp,
                                       'wind_speed': wind_speed}

        # Get images related to the location
        location_images = get_location_image(user_input)

        # Check security rating for the location (assuming city name matches)
        security_rating = security_ratings.get(city_name)

        if location_images is None:
            # No images found for the location
            no_images_message = f"No images found for {user_input}"
            return render_template("weather.html", city=city_name, forecast=list(forecasts.values()), 
                                   no_images_message=no_images_message, security_rating=security_rating) 
        else:
            return render_template("weather.html", city=city_name, forecast=list(forecasts.values()),
                                   images=location_images, security_rating=security_rating)


# Security rating dictionary (replace with your actual data source)
security_ratings = {
    "Nairobi": 82,
    "Mombasa": 79,
    "Naivasha": 87,
    "Kisumu": 90
}


@app.route('/') # Define the home route
def index():
    return render_template('index.html')


@app.route('/weather') # Define the weather route
def weather():
    user_input = request.args.get("city")
    if user_input:
        return weather_forecast(user_input)
    else:
        # If no city parameter is provided, handle accordingly
        return render_template('weather.html', error="No city parameter provided")



if __name__ == '__main__': # Check if the script is being run
    app.run(debug=True)
