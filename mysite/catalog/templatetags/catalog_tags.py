from django import template
from catalog.models import DPC_TaxonomyTerm, DPC_AcademicPage
from catalog.functions import _taxonomyTerm_objects_to_html_option_list
from catalog.functions import _academicPage_objects_to_html_dmf_list
from catalog.functions import _academicPage_parentcode_to_html_dpc_child_display
register = template.Library()

# https://docs.djangoproject.com/en/4.0/howto/custom-template-tags/
@register.inclusion_tag('tags/dmf_fp_dropdown_block_tag.html')
def dmf_fp_dropdown_block():
    online = DPC_AcademicPage.objects.filter(class_format__name='Online',).exclude(field_of_study=None).values('field_of_study__name','field_of_study__urlparam').distinct().order_by('field_of_study__name')
    campus = DPC_AcademicPage.objects.filter(class_format__name='Campus',).exclude(field_of_study=None).values('field_of_study__name','field_of_study__urlparam').distinct().order_by('field_of_study__name')
    return {'online': online,'campus': campus}


# https://docs.djangoproject.com/en/4.0/howto/custom-template-tags/
@register.inclusion_tag('tags/dmf_page_dropdown_block_tag.html')
def dmf_page_dropdown_block(*args):
    # Isn't necessary that it get keyword arguments or context (**kwargs)
    return {
        'html_field_of_study':_taxonomyTerm_objects_to_html_option_list('Field of Study',args),
        'html_class_format':_taxonomyTerm_objects_to_html_option_list('Class Format',args),
        'html_degree_type':_taxonomyTerm_objects_to_html_option_list('Degree Type',args),
        'html_program_type':_taxonomyTerm_objects_to_html_option_list('Program Type',args)
    }

# primary DMF program listing block recieves taxonomy arguments  
@register.inclusion_tag('tags/dmf_program_block.html')
def dmf_program_block(*args,**kwargs):
    sidebar = {}
    if kwargs:
        if kwargs['sidebar']:
            sidebar = kwargs['sidebar']
    return {
        'vars':args,
        'output':_academicPage_objects_to_html_dmf_list(args,sidebar=sidebar),
    }

@register.inclusion_tag('tags/dmf_program_parent.html')
def dmf_program_parent(**kwargs):
    return {
        'Parent':kwargs['Parent']
    }

@register.inclusion_tag('tags/dmf_program_child.html')
def dmf_program_child(**kwargs):
    return {
        'Child': kwargs['Child']
    }

@register.inclusion_tag('tags/dpc_child_display.html')
def dpc_child_display(parentCode):
    return {
        'parentCode': parentCode,
        ' ': _academicPage_parentcode_to_html_dpc_child_display(parentCode)
    }