from django.shortcuts import render, HttpResponse
from django.conf import settings
from django.views.generic.base import TemplateView
from catalog.models import DPC_TaxLibrary,DPC_TaxonomyTerm,DPC_AcademicPage
from datetime import datetime
from catalog.queries import get_taxonomy_libraries, get_codes, get_programs
from catalog.functions import _convert_object_array_to_html_option_list

# for JSON output
import json
from django.http import JsonResponse

# we need to pass this request
def demo(request):
    demo_headline = '<h1>Demo Page</h1>'
    demo = "demo"
    # context variables in the {} are accessible on home within {{}}
    return render(request, 'demo.html',{'demo':demo,})

# we need to pass this request
def programs(request,firstparam,secondparam):
    program_headline = '<h1>Program Page</h1>'
    # context variables in the {} are accessible on home within {{}}
    return render(request, 'programs.html',{'headline':program_headline,'firstparam':firstparam,'secondparam':secondparam})


class DPC_AcademicPageView(TemplateView):
    template_name = "AcademicPage.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['latest_articles'] = AcademicPage.objects.all()[:5]
        return context


def dmf_json(request):
    null = None
    generate_json = {
        "generated": datetime.now().strftime("%m%d%y, %H:%M:%S"),
        "taxonomy": get_taxonomy_libraries(),
        "dmf_codes" : get_codes(),
        "programs": get_programs(),
    }
    return JsonResponse(generate_json, safe=False)

# https://stackoverflow.com/questions/30417720/django-save-file-to-static-directory-from-view
# processes a call to the dmf_json() view that triggers the refresh/generation of the json file
# this json file is stored in the static folders since it doesn't change much and 
# will be 
def process_json(request):
    generate_json = {
        "generated": datetime.now().strftime("%m%d%y, %H:%M:%S"),
        "taxonomy": get_taxonomy_libraries(),
        "dmf_codes" : get_codes(),
        "programs": get_programs(),
    }
    html = '<p>The dmf.json file has been generated and is available here: <a href="/display_dmf">/display_dmf</a></p>'
    file=open(settings.STATIC_ROOT+'/'+'dmf.json','w')
    file.write(json.dumps(generate_json))
    file.close()
    return HttpResponse(html)

def display_json(request):
    return HttpResponse(open(settings.STATIC_ROOT+'/'+'dmf.json', 'r'),content_type = 'application/json; charset=utf8')