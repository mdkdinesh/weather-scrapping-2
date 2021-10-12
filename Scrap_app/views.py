import os
from django.http import HttpResponse
from django.shortcuts import render, redirect
from bs4 import BeautifulSoup
from datetime import date
import requests
import pandas as pd
import re
from .models import Weather
from urllib.request import Request, urlopen

user_agent = {
    'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36'}


# Create your views here.
def index(request):
    if request.method == "POST":
        start_date = request.POST['sd'].split('-')
        end_date = request.POST['ed'].split('-')

        end = date(int(end_date[0]), int(end_date[1]), int(end_date[2]))
        start = date(int(start_date[0]), int(start_date[1]), int(start_date[2]))
        delta = (end - start).days

        user_location = request.POST['city_name']
        url = "https://www.accuweather.com/en/search-locations?query=" + user_location
        page = requests.get(url, headers=user_agent)
        soup = BeautifulSoup(page.content, "html.parser")
        multi_locations = soup.find("div", {"class": "locations-list content-module"})
        first_link = multi_locations.find("a")['href']

        url = "https://www.accuweather.com" + first_link
        page = requests.get(url, headers=user_agent)
        soup = BeautifulSoup(page.content, "html.parser")

        page = requests.get(url, headers=user_agent)
        soup = BeautifulSoup(page.content, "html.parser")
        daily_url = "https://www.accuweather.com" + (soup.findAll("a", {"class": "subnav-item"})[2]["href"])

        url = daily_url
        page = requests.get(url, headers=user_agent)
        soup = BeautifulSoup(page.content, "html.parser")
        print("Searching : ", url)

        urls = []
        temp_url = url
        print("Reading the urls")
        for i in range(delta + 2):
            urls.append(temp_url + '?day=' + str(i))
            temp_url = url
        print("Urls Fetched\n")

        pages = []
        print("Fetching page content", end='')
        for day in urls:
            page = requests.get(day, headers=user_agent)
            soup = BeautifulSoup(page.content, "html.parser")
            pages.append(soup)
            print(".", end='')
        print("\nPages Fetched")

        # Scrapping
        df_list = []
        data = []
        for first in pages:
            date1 = first.find("div", {"class": "subnav-pagination"}).find("div").text
            temp = first.find("div", {"class": "temperature"}).text.replace("\t", '').replace("\n", '')
            day_panel = first.findAll("div", {"class": "half-day-card content-module"})[0]
            values = []
            for x in day_panel.findAll("p", {"class": "panel-item"}):
                values.append(x.find("span").text)
            max_uv_index = values[0].split(" ")[0]
            wind_direction = values[1].split(" ")[0]
            wind_speed = values[1].split(" ")[1]
            wind_gusts = values[2].split(" ")[0]
            precipitation_prob = values[3].replace("%", "")
            thunderstorm_prob = values[4].replace("%", "")
            precipitation = values[5].split(" ")[0]

            df_list = [date1.split(",")[1].strip(), user_location, temp.split("°")[0].strip(), max_uv_index,
                       wind_direction, wind_speed, wind_gusts, precipitation_prob, thunderstorm_prob, precipitation]
            data.append(df_list)

        df = pd.DataFrame(data)
        df.columns = ["Date",
                      "City", "Temperature_in_F",
                      "Max_UV_Index", "Wind_direction",
                      "Windspeed", "Gustspeed",
                      "Precipitation_prob", "Thunderstorm_prob",
                      "Precipitation"]

        df.to_csv("Scraped_weather_data.csv", index=False)
        Temperature_in_F = [x for x in df['Temperature_in_F']]
        Precipitation = [x for x in df['Precipitation']]
        Wind_direction = [x for x in df['Wind_direction']]
        Windspeed = [x for x in df['Windspeed']]
        Max_UV_Index = [x for x in df['Max_UV_Index']]
        City = [x for x in df['City']]
        Date = [x for x in df['Date']]
        (Weather.objects.all()).delete()
        for i in range(1, delta + 2):
            Weather.objects.create(
                city=City[i],
                date1=Date[i],
                temperature=Temperature_in_F[i],
                Precipitation=Precipitation[i],
                Windspeed=Windspeed[i],
                Wind_direction=Wind_direction[i],
                Max_UV_Index=Max_UV_Index[i]
            )
        return redirect('/dataset')
    return render(request, 'index.html')


def dataset(request):
    Outputs = {"Outputs": Weather.objects.all()}
    return render(request, 'dataset.html', Outputs)


def getcsv(request):
    response = HttpResponse(open('Scraped_weather_data.csv', 'rb').read(), content_type='text/csv')
    response['Content-Length'] = os.path.getsize('Scraped_weather_data.csv')
    response['Content-Disposition'] = 'attachment; filename=%s' % 'Scraped_weather_data.csv'
    return response


def get_direction(direction):
    if 348.75 < direction < 11.25:
        return "North"
    elif 11.25 < direction < 78.75:
        return "North East"
    elif 78.75 < direction < 101.25:
        return "East"
    elif 101.25 < direction < 168.75:
        return "South East"
    elif 168.75 < direction < 191.25:
        return "South"
    elif 191.25 < direction < 213.75:
        return "South West"
    elif 258.75 < direction < 281.25:
        return "West"
    else:
        return "North West"
