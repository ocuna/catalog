from django.urls import path, register_converter
from catalog.views import demo, display_json, process_json
from catalog.views import DMF_AcademicProgramList, DPC_AcademicPageDetailView
from catalog.urls_converter import DMF_url_options, DMF_TaxonomyTerm
from catalog.urls_converter import AcademicPageFacultyDept, AcademicPageSlug
from catalog.urls_converter import AcademicPagePrimaryKey

register_converter(DMF_url_options, 'options')
register_converter(DMF_TaxonomyTerm, 'TaxTerm')
register_converter(AcademicPageFacultyDept,'FDept')
register_converter(AcademicPageSlug,'APslug')
register_converter(AcademicPagePrimaryKey,'APpk')

urlpatterns = [
    path('', demo, name="demo"),
    path('display_dmf/',display_json, name='display_dmf'),
    path('process_dmf/',process_json, name='process_dmf'),
    # a set of custom converters that strictly test the urls being requested
    # DMF refers to the list system that is generated in mulitple places
    # DMF = Dynamic Marketing Funnel
    path('programs/<options:firstparam>/<TaxTerm:secondparam>',
        DMF_AcademicProgramList, name='DMFlist'),
    # recives the department (largely ignored), then the slug based on the title
    # plus the unique id = primary key = pk
    # the DetailView class in views is overriden so the .as_view() method needs
    # called from here to produce the httpRespnose or render() that is required 
    path('<FDept:dept>/<APslug:slug>/<APpk:pk>', DPC_AcademicPageDetailView.as_view(),
        name='academicpage'),
]