from django.shortcuts import render
from django.http import HttpResponse
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.conf import settings
import requests
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from weatherapp.serializer import UserSerializer, WeatherCondnSerializer
from django.views.decorators.csrf import csrf_exempt
from weatherapp.models import WeatherCondn
import logging
import json

logger = logging.getLogger(__name__)
logging.basicConfig(filename='debug.log', level=logging.DEBUG)
api_key = settings.ACCUWEATHER_API_KEY


@csrf_exempt
@api_view(['GET'])
def signup(request):
    '''
    Purpose: Creates a new user
    Input: 
    username: (mandatory) <str> User
    email: (mandatory) <str> Email
    password: (mandatory) <str> password
    Output: Status of the created User
    '''
    try:
        username = request.query_params.get('username')
        email = request.query_params.get('email')
        password = request.query_params.get('password')
        user = User.objects.create_user(username, email, password)
        user.save()
        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    except Exception as e:
        error = {'Error_code': status.HTTP_400_BAD_REQUEST,
                 'Error_Message': "Could not create user: " + str(username) + ' ' + str(email) + ' ' + str(password)}
        logger.error(e)
        return Response(json.dumps(error), status=status.HTTP_400_BAD_REQUEST)


@csrf_exempt
@api_view(['GET'])
def loginUser(request):
    '''
    Purpose: Check the credentials of the User and login
    Input: 
    username: (mandatory) <str> User
    password: (mandatory) <str> password
    Output: Status shown as success if credentials are valid. Status returned as Invalid login.
    '''
    try:
        username = request.query_params.get('username')
        password = request.query_params.get('password')
        user = authenticate(
            request._request, username=username, password=password)
        if user is not None:
            login(request, user)
            msg = {'status': "Successfully logged in"}
            return Response(msg, status=status.HTTP_200_OK)
        else:
            error = {'Error_code': status.HTTP_400_BAD_REQUEST,
                     'Error_Message': "Invalid Credentials: "+str(username)+" "+str(password)}
            logger.error(error)
            return Response(json.dumps(error), status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        error = {'Error_code': status.HTTP_400_BAD_REQUEST,
                 'Error_Message': "Something happened while trying to login. CHeck logs."}
        logger.error(e)
        return Response(json.dumps(error), status=status.HTTP_400_BAD_REQUEST)


@csrf_exempt
@api_view(['GET'])
def logoutUser(request):
    '''
    Purpose: Log out the user
    Input: No Inputs
    Output: Status shown as success if logged out, else shows an error status and message 
    '''
    try:
        logout(request)
        msg = {'status': "Successfully logged out"}
        return Response(msg, status=status.HTTP_200_OK)
    except Exception as e:
        error = {'Error_code': status.HTTP_400_BAD_REQUEST,
                 'Error_Message': "Something happened while trying to logout. CHeck logs."}
        logger.error(e)
        return Response(json.dumps(error), status=status.HTTP_400_BAD_REQUEST)


@csrf_exempt
@api_view(['GET'])
def get_regions(request):
    '''
    Purpose: Get all the regions provided by the Accuweather API
    Input: No Inputs
    Output: JSON containing all the region codes and their corresponding Names
    '''
    try:
        url = "http://dataservice.accuweather.com/locations/v1/regions?apikey="+api_key
        region_codes = requests.get(url).json()
        region_map = {region['ID']: region['EnglishName']
                      for region in region_codes}
        return HttpResponse(json.dumps(region_map), status=status.HTTP_200_OK)
    except Exception as e:
        error = {'Error_code': status.HTTP_400_BAD_REQUEST,
                 'Error_Message': "Not able to retrieve data from url" + url}
        logger.error(e)
        return Response(json.dumps(error), status=status.HTTP_400_BAD_REQUEST)


@csrf_exempt
@api_view(['GET'])
def get_countries(request):
    '''
    Purpose: Get all the countries provided by the Accuweather API
    Input: 
    region_id: (mandatory) <str> region id from the above endpoint
    Output: JSON containing the country codes and their corresponding Names for the given region
    '''
    region_id = request.query_params.get('region_id')
    try:
        url = "http://dataservice.accuweather.com/locations/v1/countries/?regionCode={}&apikey="+api_key
        country_codes = requests.get(url.format(region_id)).json()
        print(country_codes)
        country_map = {country['ID']: country['EnglishName']
                       for country in country_codes}
        return HttpResponse(json.dumps(country_map), status=status.HTTP_200_OK)
    except Exception as e:
        error = {'Error_code': status.HTTP_400_BAD_REQUEST,
                 'Error_Message': "Not able to retrieve data from url" + url}
        logger.error(e)
        return Response(json.dumps(error), status=status.HTTP_400_BAD_REQUEST)


@csrf_exempt
@api_view(['GET'])
def get_data_from_search(request):
    '''
    Purpose: Get the Current Weather condition of the given city
    Input: 
    city: (mandatory) <str> city name (Need not be an exact match)
    Output: JSON containing the current weather condition of the given city
    '''

    city = request.query_params.get('city')
    try:
        url = 'http://dataservice.accuweather.com/locations/v1/search?q={}&apikey='+api_key
        city_location = requests.get(url.format(city)).json()
        location_key = city_location[0]['Key']
        current_condn_url = "http://dataservice.accuweather.com/currentconditions/v1/{}?apikey="+api_key
        curr_condn_data = requests.get(
            current_condn_url.format(location_key)).json()
        time = curr_condn_data[0]["LocalObservationDateTime"]
        weathertxt = curr_condn_data[0]["WeatherText"]
        precipitation = "Precipitation present" if curr_condn_data[
            0]["HasPrecipitation"] == "true" else "No Precipitation"
        temp_dict = curr_condn_data[0]["Temperature"]["Metric"]
        temperature = str(temp_dict["Value"]) + " " + temp_dict["Unit"]
        link = curr_condn_data[0]["Link"]
        weathercond = WeatherCondn(city=city, time=time, weathertxt=weathertxt,
                                   precipitation=precipitation, temperature=temperature, link=link)
        weathercond.save()
        serializer = WeatherCondnSerializer(weathercond)
        return HttpResponse(json.dumps(serializer.data), status=status.HTTP_200_OK)
    except Exception as e:
        error = {'Error_code': status.HTTP_400_BAD_REQUEST,
                 'Error_Message': "Could not find the location. Please provide another search term."}
        logger.error(e)
        return Response(json.dumps(error), status=status.HTTP_400_BAD_REQUEST)
