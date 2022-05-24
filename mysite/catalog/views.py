from django.shortcuts import render, HttpResponse, get_object_or_404
from django.conf import settings
from django.views.generic import DetailView
from django.views.generic.base import TemplateView
from catalog.models import DPC_TaxLibrary,DPC_TaxonomyTerm,DPC_AcademicPage
from datetime import datetime
from catalog.queries import get_taxonomy_libraries, get_codes, get_programs
from catalog.functions import _taxonomyTerm_objects_to_html_option_list

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
def DMF_AcademicProgramList(request,firstparam,secondparam):
    program_headline = '<h1>Program Page</h1>'
    # context variables in the {} are accessible on home within {{}}
    return render(request, 'programs.html',{'headline':program_headline,'firstparam':firstparam,'secondparam':secondparam})

# this class inherits DetailView and mothods in DetailView are overridden
# to produce the content sent to the template this works 'automatically or
# abstractly' instead of the manual way to return a render(request) or
# HttpResopnse.
# https://docs.djangoproject.com/en/3.2/ref/class-based-views/generic-display/
# DetailView 
class DPC_AcademicPageDetailView(DetailView):
    template_name = 'AcademicPage.html'
    context_object_name = 'Page'

    def get_queryset(self):
        #print(self.kwargs)
        self.Page = get_object_or_404(DPC_AcademicPage, pk = self.kwargs['pk'])
        # additional filtering can be done here
        return DPC_AcademicPage.objects.filter(pk=self.Page.pk)

    # here we can add additional context that may need modifications based on
    # what is provided in kwargs (keyword dict. which is assembled from the
    # url parameters identified in urls.py
    def get_context_data(self, **kwargs):
        class_format_list = DPC_AcademicPage.objects.filter(pk=self.Page.pk).values_list('class_format__urlparam')
        field_of_study = DPC_AcademicPage.objects.filter(pk=self.Page.pk).values_list('field_of_study__urlparam')
        field_of_study_list_arg = []
        taxonomy_args = ''    
 
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        for i in class_format_list:
            if i[0] == 'campus':
                context['Campus'] = True
            if i[0] == 'online':
                context['Online'] = True
            if i[0] == 'onlineplus':
                context['OnlinePlus'] = True

        for i in field_of_study:
            field_of_study_list_arg.append(i[0])

        # add in whatever variables are necessary into the context
        context['pk'] = self.kwargs['pk']
        context['slug'] = self.kwargs['slug']
        context['dept'] = self.kwargs['dept']
        context['field_of_study_list_arg'] = tuple(field_of_study_list_arg)
        return context

'''

class DPC_AcademicPageView(TemplateView,**kwargs):
    print('DPC_AcademicPageView fired')
    template_name = "AcademicPage.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['latest_articles'] = AcademicPage.objects.all()[:5]
        return context
'''


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