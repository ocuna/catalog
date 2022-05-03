from django.urls import path
from . import views
from .views import display_json, process_json

urlpatterns = [
    path('', views.demo, name="demo"),
    path('display_dmf/',display_json, name='display_dmf'),
    path('process_dmf/',process_json, name='process_dmf')
]