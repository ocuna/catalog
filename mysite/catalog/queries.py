from catalog.models import DPC_TaxLibrary,DPC_TaxonomyTerm,DPC_AcademicPage

def get_taxonomy_libraries():
    libraries = DPC_TaxLibrary.objects.all()
    output = []

    for v in libraries:
        thisOne = {"tax_name":v.name, "tax_machine_name": v.name.lower().replace(" ","_"), "tax_desc" : v.desc} 
        output.append(thisOne) 
    return output

def get_codes():
    terms = DPC_TaxonomyTerm.objects.all().select_related('library')
    output = {}
    for v in terms:
        output[v.code] = {
            "name": v.name,
            "tax_machine_name" : v.library.name.lower().replace(" ","_"),
            "tax_name" : v.library.name,
            "url_param" : v.urlparam
        }
    return output

def get_codes_filter():
    terms = DPC_TaxonomyTerm.objects.all().select_related('library')
    output = {}
    for v in terms:
        output[v.code] = {
            "name": v.name,
            "tax_machine_name" : v.library.name.lower().replace(" ","_"),
            "tax_name" : v.library.name,
            "url_param" : v.urlparam
        }
    return output

def get_programs():
    null = None
    output = {}
    degree_type = null
    parent_code = null

    # anyting with ForignKey one-to-one relationships can have select_related to reference that model by the relationship (but only if it is published) 
    programs = DPC_AcademicPage.objects.select_related('program_type').select_related('degree_type').select_related('parent_code').filter(status="published")

    # first we cycle through all the programs that are selected
    for v in programs:
        # here we need a new allCodes list/object that can recieve codes
        # that occure in many-to-many relationships
        allCodes = []
        # every program has a program_type, so we just toss this in
        allCodes.append(v.program_type.code)
        # a many-2-many relationship query that grabs all the relationships
        # in the class_format reference - and only get the 1 field
        for c in v.class_format.all().only('code'):
            allCodes.append(c.code)
        for c in v.field_of_study.all().only('code'):
            allCodes.append(c.code)
        for c in v.faculty_department.all().only('code'):
            allCodes.append(c.code)

        # check if the parent_code is empty
        if v.parent_code is not None:
            # if it is not empty get that paren_code's unique code
            parent_code = v.parent_code.unique_program_code
        if v.degree_type is not None:
            degree_type = v.degree_type.name
            allCodes.append(v.degree_type.code)
        output[v.unique_program_code] = {
            "path": null,
            "nid" : null,
            "title": v.title,
            "parent": parent_code,
            "type": degree_type,
            "dmf_codes" : allCodes
        }
    #print(output)
    return output