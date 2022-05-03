from django.urls import path, register_converter
from . import views
from .views import display_json, process_json, programs
from .urls_converter import dmf_url_options, dmf_url_taxonomy

register_converter(dmf_url_options, 'options')
register_converter(dmf_url_taxonomy, 'taxterm')

urlpatterns = [
    path('', views.demo, name="demo"),
    path('display_dmf/',display_json, name='display_dmf'),
    path('process_dmf/',process_json, name='process_dmf'),
    # a set of custom converters that strictly test the urls being requested
    path('programs/<options:firstparam>/<taxterm:secondparam>',programs, name='programs')
]