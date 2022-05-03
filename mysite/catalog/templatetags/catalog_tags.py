from django import template
from catalog.models import DPC_TaxonomyTerm
register = template.Library()

# https://docs.djangoproject.com/en/4.0/howto/custom-template-tags/
@register.inclusion_tag('tags/dmf_fp_dropdown_block_tag.html', takes_context=True)
def dmf_fp_dropdown_block(context):
    online = campus = {}
    for i,v in enumerate(DPC_TaxonomyTerm.objects.filter(library__name='Field of Study')):
        # these need futher filterd to check to see which Degree Program Pages
        # are published that have 'online' or campus as their program type
        online[i] = {'name':v.name,'urlparam':v.urlparam }
        campus[i] = {'name':v.name,'urlparam':v.urlparam }
    return {'online': online,'campus': campus, 'context':context }


# https://docs.djangoproject.com/en/4.0/howto/custom-template-tags/
@register.inclusion_tag('tags/dmf_page_dropdown_block_tag.html', takes_context=True)
def dmf_page_dropdown_block(context):
    return {'context':context }
 