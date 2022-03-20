from django.db import models
from datetime import datetime

get_cur_time = datetime.now().strftime('%m/%d/%Y %I:%M:%S %p')

class WeatherCondn(models.Model):
    city = models.CharField(max_length=100,null=False)
    time = models.CharField(max_length=50,default=get_cur_time)
    weathertxt = models.CharField(max_length=100,null=True)
    precipitation = models.CharField(max_length=100,null=True)
    temperature = models.CharField(max_length=10,null=True)
    link = models.CharField(max_length=500,null=True)

