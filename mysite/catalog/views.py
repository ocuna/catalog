from django.shortcuts import render
from django.views.generic.base import TemplateView
from catalog.models import DPC_AcademicPage

# we need to pass this request
def demo(request):
	demo_headline = '<h1>Demo Page</h1>'
	# context variables in the {} are accessible on home within {{}}
	return render(request, 'demo.html',
        {
            'demo':demo,
        })


class DPC_AcademicPageView(TemplateView):
    template_name = "AcademicPage.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['latest_articles'] = AcademicPage.objects.all()[:5]
        return context