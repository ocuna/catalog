from django.db.models import Q,F,Value,Subquery
from django.db.models.functions import Concat
from catalog.models import DPC_TaxLibrary, DPC_TaxonomyTerm, DPC_AcademicPage

# calls the DB for all taxonomy terms matching the tax term
# from: _convert_object_array_to_html_option_list()
def _taxonomyTerm_objects_to_html_option_list(tax_term='',url_args=None):
    # print(url_args)
    preprocesshtml = ''
    html = ''
    selected = ''
    default_all = True
    tax_machine_name = ''
    output = []
    terms = (DPC_TaxonomyTerm
        .objects
        .all()
        .select_related('library')
        .filter(library__name=tax_term)
        .order_by('name'))
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
        if(v['url_param'] in url_args):
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


# calls the DB for all programs that match the args
# always sorts them in a specific way: Masters,BA,BS,AA,AS,Minor,Certificate
# collects parent programs with their child programs
# complex filtering and parent/child checks sometimes produce LONG sql queries
# there is room for optimization of queries, but may require mulitple queries
# or a refactoring of the database stucture.
# unfortunaltey child_search parameter needed be hard-set to account for
# instances where one of these parameteres was searched for creating the need
# to union parents appropriately with searched-for child programs. 
def _academicPage_objects_to_html_dmf_list(args):
    filter_q1 = Q() # empty Q object will be filled later
    filter_q2 = Q() # empty Q object will be filled later
    unique_program_codes = set()
    enumerate_args = {}
    Parents = {}
    Children = {}
    html = ''

    # Did the user request one of these search parameters?  They only will ever
    # belog to childen of degrees.  When this is the case these values are in
    # the searches a very different query and assemply of parent degrees of
    # these child parameters.  This exception creates very large queries
    child_searches = ('concentration','license','endorsement')

    # if arguments are passed into this function, we need to search the db
    # and simply go through each field that could potentially contain the arg
    # within the pages table
    if args:
        thesePages = {}
        Terms = DPC_TaxonomyTerm.objects.all()
        # loop through each arg passed in from the template tag
        for i,arg in enumerate(args):
            enumerate_args[i] = arg
            # Basically merges dictionaries with or and equals operators
            # this sets up a filter that is later used to transform the urlparam
            # into the DB record that is referenced by the pages``
            # breaking this up because otherwise the filter/query is just too
            # impossible to read/write
            filter_q1 |= Q(urlparam=arg)

        # Clean up the terms by making sure there are no duplicates
        Terms = Terms.filter(filter_q1).distinct()

        # Start by grabbing all pages that currenlty exist as published
        # Note: this sort contains both children and parents
        Pages_qs1 = (DPC_AcademicPage.objects.all()
            .filter(status='published'))

        for i,term in enumerate(Terms):
            # each time a term is iterated from the prior arguments
            # filter teach term by each possible field using 'OR' opperator
            Pages_qs1 = Pages_qs1.filter(Q(degree_type__name=term) |
                Q(field_of_study__name=term) |
                Q(program_type__name=term) |
                Q(faculty_department__name=term) |
                Q(class_format__name=term))

        # detect if args and child_searches have intersecting values with set()
        # there is a possibility the user searched for a child and not 
        # a parent.  To make the parents show up do another search on the 
        # results so far.  Make a copy of the queryset and process it
        # this set of queries are not compatible with later order_by filters
        # this is likely doing someting very very horrendous - the 
        if set(args) & set(child_searches):
            Pages_qs2 = Pages_qs1

            for i,page in enumerate(Pages_qs1):

                # does this page have a parent?  Add it, but don't dubplicate
                if page.parent_code is not None:
                    # this can generate a massive amount of codes,
                    # force to uniques only
                    unique_program_codes.add(page.parent_code.unique_program_code)

            # now, build the filter we will later use, but only if there are
            # unique_program_codes.  If no codes, then it's an empty search
            if unique_program_codes:
                for i,v in enumerate(unique_program_codes):
                    filter_q2 |= Q(unique_program_code=v)


                Parents_of_children = DPC_AcademicPage.objects.filter(filter_q2).distinct()
                # then sort them by their specific ascending weight
                # Unite the parents of children and the pages
                Pages = Pages_qs1.union(Pages_qs1,Parents_of_children)

                # PLEASENOTE!!!
                # this is likely doing something completely horrendous by not
                # simply hitting the DB, and then cycling the results to hit
                # the database again.  I'm not going to performance test this
                # however because the likelyhood that this is going to be utilized
                # often is very low.  People will almost never search for children 
                # such as concentrations, endorsements or license...and expect to
                # get parents ... they will search parent degree programs first.
                # print(Pages.query)
            else: 
                #print('Empty Query')
                html = "<p>Sorry, no programs that fit the search parameters: {}</p>".format(args)
        
        # if the args and child_searches do not intersect, we can order by the
        # pages as expected because there is no complex union required
        else:
            Parents = (Pages_qs1.order_by(F('degree_type__weight').asc(nulls_last=True),
                F('program_type__weight').asc(nulls_last=True),
                F('class_format__weight').asc(nulls_last=True),
                'title').distinct())
   
    # If there are Academic Degree Pages to show, loop through all pages
    # looking for children of these parents.
    if Parents:
        # Collect all children by checking if the parent code is NOT null
        # collect only the objects that HAVE parent code = children
        Children = (DPC_AcademicPage
            .objects
            .filter(status='published')
            .filter(parent_code__isnull=False) # Parent Code must exist (IS A CHILD)
            .exclude(Q(program_type__name='Degree') | Q(program_type__name='Minor')) # Program Type can't be a Degree or Minor
            .order_by('degree_type__weight',
                'program_type__weight',
                'class_format__weight',
                'title')
            .distinct()) # Order Weight by lightest to heaviest then by Title
        
        for pi,pv in enumerate(Parents):
            # it's possible there is a child page in this loop, skip it because
            # you can't do a .distinct() after the union:
            # Pages = Pages_qs1.union(Pages_qs1,Parents_of_children)|2
            if pv.parent_code is not None:
                continue
            #start the HTML with an open tag
            html += '<li>' + pv.title
            # loop through each child degree, does the parent page match?
            for ci,cv in enumerate(Children):
                if pv == cv.parent_code: 
                    html += '<br>' + cv.title
            #close the loop
            html += '</li>'

    return { 'Parents':Parents, 'children':Children, 'html':html }


def _academicPage_objects_to_html_dmf_list_complete(args):
    Parents =  (DPC_AcademicPage.objects.all()
        .prefetch_related(
            Prefetch('field_of_study'),
            Prefetch('class_format'),
            Prefetch('faculty_department'))
        .annotate(
            degree_type__code=F('degree_type__code'),
            program_type__code=F('program_type__code'))
        .filter(Q(program_type__name='Concentration')))
    
    Parents_And_Kids = (DPC_AcademicPage.objects.all()
        .filter(parent_code__isnull=True)
        .select_related('parent_code')
        .prefetch_related('parent_code__parent_code')[1]
        .dpc_academicpage_set
        .values('title'))


    # wanna get the codes?
    # P.objects.all().filter(parent_code__isnull=True)
    #   .select_related('parent_code')
    #   .prefetch_related('parent_code__parent_code')[1]
    #   .dpc_academicpage_set
    #   .values_list('faculty_department__code')

    # WOW - MEGA LIST THIS??
    # this = set(P.objects.all().filter(parent_code__isnull=True).select_related('parent_code').prefetch_related('parent_code__parent_code')[1].dpc_academicpage_set.values_list('faculty_department__code')) | set(P.objects.all().filter(parent_code__isnull=True).select_related('parent_code').prefetch_related('parent_code__parent_code')[1].dpc_academicpage_set.values_list('class_format__code')) | set(P.objects.all().filter(parent_code__isnull=True).select_related('parent_code').prefetch_related('parent_code__parent_code')[1].dpc_academicpage_set.values_list('field_of_study__code'))

    # this is better, it just needs refeind by SET()
    # this = set(P.objects.all().filter(parent_code__isnull=True).select_related('parent_code').prefetch_related('parent_code__parent_code')[1].dpc_academicpage_set.values_list('faculty_department__code','class_format__code','field_of_study__code','program_type__code','degree_type__code'))

    # print(P.objects.all().prefetch_related(Prefetch('field_of_study'),Prefetch('class_format'),Prefetch('faculty_department')).annotate(degree_type__code=F('degree_type__code'),program_type__code=F('program_type__code')).filter(Q(program_type__name='Concentration')).query)
    # print(P.objects.all().prefetch_related(Prefetch('field_of_study'),Prefetch('class_format'),Prefetch('faculty_department')).annotate(degree_type__code=F('degree_type__code'),program_type__code=F('program_type__code')).filter(Q(program_type__name='Concentration'))[3].parent_code.unique_program_code)

    # print(P.objects.all().annotate(child_record=Subquery(P.objects.filter(parent_code__isnull=False),filter())))
    # doesn't actually work ... this will look in the database for a single code of the child that is related and associate that single code with annotate(child_record) 
    # print(P.objects.all().annotate(child_record=Subquery(P.objects.all().filter(parent_code__isnull=False).filter(parent_code=OuterRef('unique_program_code')).filter().values_list('unique_program_code')))[1].child_record)

    # GOT IT!

    # P.objects.all().filter(parent_code__isnull=True).select_related('parent_code').prefetch_related('parent_code__parent_code')[1].dpc_academicpage_set.values('title')