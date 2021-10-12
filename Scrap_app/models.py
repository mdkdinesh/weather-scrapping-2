from django.db import models


# Create your models here.

class Weather(models.Model):
    date1 = models.CharField(max_length=20,null=True)
    city = models.CharField(max_length=25,null=True)
    temperature = models.FloatField(default=0.0)
    Precipitation = models.FloatField(default=0.0)
    Windspeed = models.FloatField(default=0.0)
    Wind_direction = models.CharField(max_length=5,null=True)
    Max_UV_Index = models.FloatField(default=0.0)
