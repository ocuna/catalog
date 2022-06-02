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

# Primary DMF program listing block recieves taxonomy arguments and urlparam
# Works with multiple arguments as filters by default
#  {% dmf_program_block 'delimited_string' 'criminal-justice degree' %}

# Delimited String also works with Union and specific Exclusions
#  {% dmf_program_block 'delimited_string' 'criminal-justice degree union exclude:certificate' %}

# Carries the current arguments to the same function for re-use
#  {% dmf_program_block field_of_study_list_arg %}

# Can mix a tuple and multiple text values for use like:
#  {% dmf_program_block field_of_study_list_arg 'union' 'bible' 'exclude:certificate' 'exclude:minor' %}

# Arguments resetbutton and program key change format:
#  {% dmf_program_block field_of_study_list_arg 'resetbutton' 'programkey' %}

@register.inclusion_tag('tags/dmf_program_block.html')
def dmf_program_block(*args):
    # if the *args have been compiled twice because of tag-nesting, reduce to a
    # easy tuple each time
    cleanargs = []
    for i,arg in enumerate(args):
        if isinstance(args[i],tuple):
            for i,t in enumerate(args[i]):
                cleanargs.append(t)
        else:
            cleanargs.append(arg)

    return {
        # very complex function receives args and processes them...
        # see notes in functions.py
        'output':_academicPage_objects_to_html_dmf_list(cleanargs),
    }

# almost exactly like dmf_program_block
# template tag is different as parents expand without children
@register.inclusion_tag('tags/dmf_program_parent_expanding_block.html')
def dmf_program_parent_expanding_block(*args):
    # if the *args have been compiled twice because of tag-nesting, reduce to a
    # easy tuple each time
    cleanargs = []
    for i,arg in enumerate(args):
        if isinstance(args[i],tuple):
            for i,t in enumerate(args[i]):
                cleanargs.append(t)
        else:
            cleanargs.append(arg)
    print(cleanargs)
    return {
        # very complex function receives args and processes them...
        # see notes in functions.py
        'output':_academicPage_objects_to_html_dmf_list(cleanargs),
    }

@register.inclusion_tag('tags/dmf_program_parent.html')
def dmf_program_parent(**kwargs):
    return {
        'Parent':kwargs['Parent']
    }

@register.inclusion_tag('tags/dmf_program_parent_expanding.html')
def dmf_program_parent_expanding(**kwargs):
    return {
        'Parent':kwargs['Parent']
    }

@register.inclusion_tag('tags/dmf_program_child.html')
def dmf_program_child(**kwargs):
    return {
        'Child': kwargs['Child']
    }

@register.inclusion_tag('tags/dmf_child_display.html')
def dmf_child_display(parentCode):
    return {
        'childObject': _academicPage_parentcode_to_html_dpc_child_display(parentCode),
    }