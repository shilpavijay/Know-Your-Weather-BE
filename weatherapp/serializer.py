from rest_framework import serializers
from django.contrib.auth.models import User
from weatherapp.models import WeatherCondn

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'

class WeatherCondnSerializer(serializers.ModelSerializer):
    class Meta:
        model = WeatherCondn
        fields = '__all__'        