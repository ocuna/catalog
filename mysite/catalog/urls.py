from django.urls import path, register_converter
from . import views
from .views import display_json, process_json, programs, DPC_AcademicPageView
from .urls_converter import dmf_url_options, dmf_url_taxonomy, dmf_url_academic_page

register_converter(dmf_url_options, 'options')
register_converter(dmf_url_taxonomy, 'taxterm')
register_converter(dmf_url_academic_page,'facultyDepartment')

urlpatterns = [
    path('', views.demo, name="demo"),
    path('display_dmf/',display_json, name='display_dmf'),
    path('process_dmf/',process_json, name='process_dmf'),
    # a set of custom converters that strictly test the urls being requested
    path('programs/<options:firstparam>/<taxterm:secondparam>', programs, name='programs'),
    # recives the department (largely ignored), then the slug based on the title
    # plus the unique id = primary key = pk
    path('<facultyDepartment:dept>/<slug:slug>/<int:pk>', DPC_AcademicPageView, name='academicpage'),
]