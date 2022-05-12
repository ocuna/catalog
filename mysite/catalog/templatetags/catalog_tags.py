from django import template
from catalog.models import DPC_TaxonomyTerm, DPC_AcademicPage
from catalog.functions import _taxonomyTerm_objects_to_html_option_list
from catalog.functions import _academicPage_objects_to_html_dmf_list
from catalog.functions import _academicPage_objects_to_html_dmf_list_complete
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
        'html_class_type':_taxonomyTerm_objects_to_html_option_list('Class Type',args),
        'html_degree_type':_taxonomyTerm_objects_to_html_option_list('Degree Type',args),
        'html_program_type':_taxonomyTerm_objects_to_html_option_list('Program Type',args)
    }

@register.inclusion_tag('tags/dmf_program_block.html')
def dmf_program_block(*args):
    return {
        'vars':args,
        'output':_academicPage_objects_to_html_dmf_list_complete(args),
        #'dict':_academicPage_objects_to_html_dmf_list(args),
    }

@register.inclusion_tag('tags/dmf_program_parent.html')
def dmf_program_parent(*args,**kwargs):
    return {
        'Parent':kwargs['Parent'],
        'Children': kwargs['Children']
    }

@register.inclusion_tag('tags/dmf_program_child.html')
def dmf_program_child(**kwargs):
    return {
        'Child': kwargs['Child']
    }