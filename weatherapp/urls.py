from django.urls import path, include
from . import views


urlpatterns = [
    path('api/v1/search/', views.get_data_from_search),
    path('api/v1/signup', views.signup),
    path('api/v1/login', views.loginUser),
    path('api/v1/logout', views.logoutUser),
    path('api/v1/region', views.get_regions),
    path('api/v1/country', views.get_countries),
]
