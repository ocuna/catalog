from django.db.models import Q,F,Value,Subquery,Prefetch
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
    html = ''
    # these lists are formed after for loops process the contents and then 
    # attach specific data that is formatted for the templates downstreamm 
    ParentsAssembled = []
    ChildrenAssembled = []

    # there will always be args because urls_converter.py shoud catch it ...
    # but just in case...
    if args:
        # this is a complex query that needs to request multiple related tables
        # Prefetch calls the tables in advance so they don't get hit each time
        # a record is request.  this is also doing to the child relationship as
        # matched on the parent_code which gets the chidlern of this parent
        # it is important to note that the childern, even thought requested through
        # the prefetch_related(parent_code) request still need their own query
        # below because they need looped and placed on a different tempate and it 
        # is simply easier to loop that separately if the code matches then to 
        # pre-load all the necessary information into a parent object that could
        # hold it. 
        Parents_PreFetch_Kids = (DPC_AcademicPage.objects.all()
            .filter(parent_code__isnull=True)
            .filter(status='published')
            .prefetch_related(
                Prefetch('field_of_study'),
                Prefetch('class_format'),
                Prefetch('faculty_department'))
            .select_related('parent_code')
            .order_by(F('degree_type__weight').asc(nulls_last=True),
                    F('program_type__weight').asc(nulls_last=True),
                    F('class_format__weight').asc(nulls_last=True),
                    'title')
            .prefetch_related('parent_code__parent_code'))

        # this separate query is simply pulling only children which will need
        # later looped based on their parent_code
        Children = (DPC_AcademicPage
            .objects
            .filter(status='published')
            .filter(parent_code__isnull=False) # Parent Code must exist (IS A CHILD)
            .exclude(
                Q(program_type__name='Degree') | # Can't be a Degree
                Q(program_type__name='Minor')) # Can't be a Minor
            .order_by('degree_type__weight',
                'program_type__weight',
                'class_format__weight',
                'title')  # Order Weight by lightest to heaviest then by Title
            .distinct())  # make sure we don't get doubles for any reason

        for i,arg in enumerate(args):
            if(arg != 'discover' and arg != 'all'):
                # each time a term is iterated from the prior arguments
                # filter each term by each possible field using 'OR' opperator
                # set up the Parents_PreFetch_Kids 
                Parents_PreFetch_Kids = Parents_PreFetch_Kids.filter(
                    Q(degree_type__urlparam=arg) |
                    Q(field_of_study__urlparam=arg) |
                    Q(program_type__urlparam=arg) |
                    Q(faculty_department__urlparam=arg) |
                    Q(class_format__urlparam=arg))

        Parents = (Parents_PreFetch_Kids
            .order_by(F('degree_type__weight').asc(nulls_last=True),
                F('program_type__weight').asc(nulls_last=True),
                F('class_format__weight').asc(nulls_last=True),
                'title')
            .distinct())
        
        # this loops through the Children and assembles their taxonomy codes
        # This is simliar but more simple then how the parents work 
        for ci,cv in enumerate(Children):
            childCodeString = ''
            childCodeList = []
            childCodeSet = set()

            for i,v in enumerate(cv.field_of_study.values_list('code')):
                for ii,vv in enumerate(v):
                    if vv :
                        childCodeSet.add(vv)

            for i,v in enumerate(cv.faculty_department.values_list('code')):
                for ii,vv in enumerate(v):
                    if vv :
                        childCodeSet.add(vv)

            for i,v in enumerate(cv.class_format.values_list('code')):
                for ii,vv in enumerate(v):
                    if vv :
                        childCodeSet.add(vv)

            if cv.program_type:
                childCodeSet.add(cv.program_type.code)

            if cv.degree_type:
                childCodeSet.add(cv.degree_type.code)


            cv.childCodeSet = childCodeSet

            # need to pipe-deliniate this for use in HTML
            for i,v in enumerate(cv.childCodeSet):
                childCodeString += v + '|'

            # remove the last charcter "|" and attach the string to the parent
            cv.childCodeString = childCodeString.rstrip(childCodeString[-1])
            ChildrenAssembled.append(cv)

        # this loops through the Parents and assembles codes from both parents
        # and children.  The HTML templates for sorting require all codes from
        # both to show on parents as well as children
        for pi,pv in enumerate(Parents):
            parentCodeString = ''
            parentCodeList = []
            parentCodeSet = set()
            parentDegreeTypeCode = ''
            parentDegreeTypeString = ''
            parentDegreeTypeURL = ''
            parentCampus = False
            parentOnline = False
            parentOnlinePlus = False
            parentCampus = False
            parentOnline = False
            parentOnlinePlus = False

            # it's possible there is a child page in this loop, skip it because
            # you can't do a .distinct() after the union:
            # Pages = Pages_qs1.union(Pages_qs1,Parents_of_children)|2
            if pv.dpc_academicpage_set:
                # deep-dive all the codes that exist within all the children of
                # the parent.  Add those codes to the child as a list and to
                # the parent as well  
                vlist = pv.dpc_academicpage_set.values_list('faculty_department__code','class_format__code','field_of_study__code','program_type__code','degree_type__code')
                for i,v in enumerate(vlist):
                    for ii,vv in enumerate(v):
                        if vv :
                            parentCodeSet.add(vv)
                
            # after all the children are done, get all the code values that
            # the parent may hold and add them just to the parentCodeSet
            #parentCodeList.append(pv.values_list('field_of_study'))
            for i,v in enumerate(pv.field_of_study.values_list('code')):
                for ii,vv in enumerate(v):
                    if vv :
                        parentCodeSet.add(vv)

            for i,v in enumerate(pv.faculty_department.values_list('code')):
                for ii,vv in enumerate(v):
                    if vv :
                        parentCodeSet.add(vv)

            for i,v in enumerate(pv.class_format.values_list('code')):
                for ii,vv in enumerate(v):
                    if vv :
                        if vv == 'F_CAMP':
                            parentCampus = True
                        if vv == 'F_ONLI':
                            parentOnline = True
                        if vv == 'F_VIRT':
                            parentOnlinePlus = True
                        parentCodeSet.add(vv)

            if pv.degree_type:
                parentDegreeTypeCode = pv.degree_type.code
                parentCodeSet.add(pv.degree_type.code)
                if pv.degree_type.code == 'DT_MAST':
                    parentDegreeTypeString = 'M'
                    parentDegreeTypeURL = pv.degree_type.urlparam
                if pv.degree_type.code == 'DT_BACA':  
                    parentDegreeTypeString = 'BA'
                    parentDegreeTypeURL = pv.degree_type.urlparam
                if pv.degree_type.code == 'DT_BACS':
                    parentDegreeTypeString = 'BS'
                    parentDegreeTypeURL = pv.degree_type.urlparam
                if pv.degree_type.code == 'DT_ASSA':
                    parentDegreeTypeString = 'AA'
                    parentDegreeTypeURL = pv.degree_type.urlparam
                if pv.degree_type.code == 'DT_ASSS':
                    parentDegreeTypeString = 'AS'
                    parentDegreeTypeURL = pv.degree_type.urlparam


            if pv.program_type:
                parentCodeSet.add(pv.program_type.code)
                if pv.program_type.code == 'PT_MINO':
                    parentDegreeTypeCode = pv.program_type.code
                    parentDegreeTypeString = 'MINOR'
                    parentDegreeTypeURL = pv.program_type.urlparam
                if pv.program_type.code == 'PT_CERT':
                    parentDegreeTypeCode = pv.program_type.code
                    parentDegreeTypeString = 'CERTIFICATE'
                    parentDegreeTypeURL = pv.program_type.urlparam


            pv.parentCodeSet = parentCodeSet
            pv.parentCampus = parentCampus
            pv.parentOnline = parentOnline
            pv.parentOnlinePlus = parentOnlinePlus
            pv.parentDegreeTypeCode = parentDegreeTypeCode
            pv.parentDegreeTypeString = parentDegreeTypeString
            pv.parentDegreeTypeURL = parentDegreeTypeURL
            
            # need to pipe-deliniate this for use in HTML
            for i,v in enumerate(pv.parentCodeSet):
                parentCodeString += v + '|'

            # remove the last charcter "|" and attach the string to the parent
            pv.parentCodeString = parentCodeString.rstrip(parentCodeString[-1])

            # add this new parent object with the
            ParentsAssembled.append(pv)
    else:
        # there should always be arguments
        # or the urls_converter.py should fail.
        pass

    # for ci,cv in enumerate(ChildrenAssembled):
        #print(cv.parent_code.unique_program_code) 

    return { 'Parents':ParentsAssembled, 'Children':ChildrenAssembled, 'html':html }
    # GOT IT!

    # P.objects.all().filter(parent_code__isnull=True).select_related('parent_code').prefetch_related('parent_code__parent_code')[1].dpc_academicpage_set.values('title')


'''
html += '<li>' + pv.title + '<small> Codes:' + parentCodeString  + '</small>'
# loop through each child degree, does the parent page match?
for ci,cv in enumerate(ChildrenAssembled):
    if pv == cv.parent_code: 
        html += '<br>' + cv.title
#close the loop
html += '</li>'
'''

    ###  FOR CODES
    # WOW - MEGA LIST THIS??
    # this = set(P.objects.all().filter(parent_code__isnull=True).select_related('parent_code').prefetch_related('parent_code__parent_code')[1].dpc_academicpage_set.values_list('faculty_department__code')) | set(P.objects.all().filter(parent_code__isnull=True).select_related('parent_code').prefetch_related('parent_code__parent_code')[1].dpc_academicpage_set.values_list('class_format__code')) | set(P.objects.all().filter(parent_code__isnull=True).select_related('parent_code').prefetch_related('parent_code__parent_code')[1].dpc_academicpage_set.values_list('field_of_study__code'))

    # this is better, it just needs refeind by SET()
    # this = set(P.objects.all().filter(parent_code__isnull=True).select_related('parent_code').prefetch_related('parent_code__parent_code')[1].dpc_academicpage_set.values_list('faculty_department__code','class_format__code','field_of_study__code','program_type__code','degree_type__code'))

    # print(P.objects.all().annotate(child_record=Subquery(P.objects.filter(parent_code__isnull=False),filter())))
    # doesn't actually work ... this will look in the database for a single code of the child that is related and associate that single code with annotate(child_record) 
    # print(P.objects.all().annotate(child_record=Subquery(P.objects.all().filter(parent_code__isnull=False).filter(parent_code=OuterRef('unique_program_code')).filter().values_list('unique_program_code')))[1].child_record)




# DON"T NEED REALLY
    # print(P.objects.all().prefetch_related(Prefetch('field_of_study'),Prefetch('class_format'),Prefetch('faculty_department')).annotate(degree_type__code=F('degree_type__code'),program_type__code=F('program_type__code')).filter(Q(program_type__name='Concentration')).query)
    # print(P.objects.all().prefetch_related(Prefetch('field_of_study'),Prefetch('class_format'),Prefetch('faculty_department')).annotate(degree_type__code=F('degree_type__code'),program_type__code=F('program_type__code')).filter(Q(program_type__name='Concentration'))[3].parent_code.unique_program_code)


