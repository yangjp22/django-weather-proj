from django.conf import settings
import requests
from urllib.parse import quote_plus
import random
import pandas as pd
import time


def current(city):
    city_input = quote_plus(city)
    token = random.choice(settings.KEYS)
    currentUrl = "https://api.openweathermap.org/data/2.5/weather?q={}&units=metric&appid={}".format(
        city_input, token)
    response = requests.get(currentUrl).json()
    response_time = response['dt'] if "dt" in response else int(time.time())
    returnDict = {'city': city,
                  "description": response['weather'][0]['description'] if "weather" in response else "",
                  'temperature': response['main']['temp'] if "main" in response else 27.5,
                  'icon': response['weather'][0]['icon'] if "weather" in response else "",
                  'time': time.strftime('%Y-%m-%d', time.localtime(response_time)),
                  }
    return returnDict


def forecast(city):
    city_input = quote_plus(city)
    token = random.choice(settings.KEYS)
    forecastUrl = 'http://api.openweathermap.org/data/2.5/forecast?q={}&units=metric&appid={}'.format(
        city_input, token)
    response = requests.get(forecastUrl)
    if response.status_code == 404:
        result = None
    else:
        response = response.json()
        returnDict = {'city': city,
                      "description": [each['weather'][0]['description'] for each in response['list']],
                      'temperature': [each['main']['temp'] for each in response['list']],
                      'icon': [each['weather'][0]['icon'] for each in response['list']],
                      'time': [each['dt_txt'] for each in response['list']],
                      }
        dataframe = pd.DataFrame(returnDict)
        dataframe['time'] = dataframe['time'].str.split(' ', expand=True)[0]
        desription = dataframe[['time', 'description']].groupby(
            'time').agg(lambda x: x.mode()[0]).reset_index()
        icon = dataframe[['time', 'icon']].groupby(
            'time').agg(lambda x: x.mode()[0]).reset_index()
        temperature = dataframe[['time', 'temperature']].groupby(
            'time').agg(lambda x: x.mean().round(2)).reset_index()

        result = desription.merge(icon, on='time')
        result = result.merge(temperature, on='time')
        result['city'] = city
        result = result.to_dict(orient='records')

        now = current(city)
        result.insert(0, now)

    return result
