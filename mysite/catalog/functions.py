from catalog.models import DPC_TaxLibrary, DPC_TaxonomyTerm, DPC_AcademicPage

# calls the DB for all taxonomy terms matching the tax term
def _convert_object_array_to_html_option_list(tax_term='',url_args=None):
    preprocesshtml = ''
    html = ''
    selected = ''
    default_all = True
    tax_machine_name = ''
    output = []
    terms = DPC_TaxonomyTerm.objects.all().select_related('library').filter(library__name=tax_term).order_by('name')
    for v in terms:
        output.append ({
            "code": v.code,
            "name": v.name,
            "tax_machine_name" : v.library.name.lower().replace(" ","_"),
            "tax_name" : v.library.name,
            "url_param" : v.urlparam
        })
        tax_machine_name = v.library.name.lower().replace(" ","_")
    for i,v in enumerate(output):
        if(url_args == v['url_param']):
            selected = 'selected'
            default_all = False
        else :
            selected = ''
        preprocesshtml += '<option id="{}" class="{} dmf-hide" value ="{}" {}>{}</option>'.format(
            v['code'],v['tax_machine_name'] +"-" + v['url_param'],v['code'],selected,v['name']
        )
    if (default_all):
        html = '<option id="'+tax_machine_name+'-all" class="all" value="--" selected > ~ all </option>' + preprocesshtml
    else:
        html = '<option id="'+tax_machine_name+'-all" class="all" value="--" > ~ all </option>' + preprocesshtml

    return html



