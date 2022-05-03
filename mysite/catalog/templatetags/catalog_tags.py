from django import template
from catalog.models import DPC_TaxonomyTerm, DPC_AcademicPage
from catalog.functions import _convert_object_array_to_html_option_list
register = template.Library()

# https://docs.djangoproject.com/en/4.0/howto/custom-template-tags/
@register.inclusion_tag('tags/dmf_fp_dropdown_block_tag.html', takes_context=True)
def dmf_fp_dropdown_block(context):
    online = DPC_AcademicPage.objects.filter(class_format__name='Online',).exclude(field_of_study=None).values('field_of_study__name','field_of_study__urlparam').distinct().order_by('field_of_study__name')
    campus = DPC_AcademicPage.objects.filter(class_format__name='Campus',).exclude(field_of_study=None).values('field_of_study__name','field_of_study__urlparam').distinct().order_by('field_of_study__name')
    for v in enumerate(online):
        print(v)
    return {'online': online,'campus': campus, 'context':context }


# https://docs.djangoproject.com/en/4.0/howto/custom-template-tags/
@register.inclusion_tag('tags/dmf_page_dropdown_block_tag.html', takes_context=True)
def dmf_page_dropdown_block(context):
    return {
        'html_field_of_study':_convert_object_array_to_html_option_list('Field of Study',None),
        'html_class_type':_convert_object_array_to_html_option_list('Class Type',None),
        'html_degree_type':_convert_object_array_to_html_option_list('Degree Type',None),
        'html_program_type':_convert_object_array_to_html_option_list('Program Type',None),
        'context':context
    }
 