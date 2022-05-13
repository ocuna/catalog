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


# calls the DB for all programs and then filters them to  match the args
# always sorts them in a specific way: Masters,BA,BS,AA,AS,Minor,Certificate
# collects parent programs with their child programs.  This function creates 
# vars specifically sent to the templates dmf_program_block, dmf_program_parent
# and dmf_program_child.  Some vars are designed to create class styles instead
# of heavily loading logic into the templates themselves
def _academicPage_objects_to_html_dmf_list(args):
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
            .filter(parent_code__isnull=False) # Parent Code exists: IS A CHILD
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
                # get a cont of the children - useful later to trigger the
                # template for children if they exist and not waste time 
                # looking through all children for each parent
                pv.childrenCount = pv.dpc_academicpage_set.count()
                # deep-dive all the codes that exist within all the children of
                # the parent.  Add those codes to the child as a list and to
                # the parent as well  
                vlist = pv.dpc_academicpage_set.values_list('faculty_department__code',
                    'class_format__code',
                    'field_of_study__code',
                    'program_type__code',
                    'degree_type__code')
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
                        # a few cases here trigger class styles on the template
                        if vv == 'F_CAMP':
                            parentCampus = True
                        if vv == 'F_ONLI':
                            parentOnline = True
                        if vv == 'F_VIRT':
                            parentOnlinePlus = True
                        parentCodeSet.add(vv)


            # this is simply a case-based system designed to create classes and
            # on the template it's passed to for proper styling based on the
            # degree or program type below 
            if pv.degree_type:
                parentDegreeTypeCode = pv.degree_type.code
                parentCodeSet.add(pv.degree_type.code)
                if pv.degree_type.code == 'DT_MAST':
                    parentDegreeTypeString = 'M'
                    parentDegreeTypeCSSTag = 'degree'
                    parentDegreeTypeURL = pv.degree_type.urlparam
                if pv.degree_type.code == 'DT_BACA':  
                    parentDegreeTypeString = 'BA'
                    parentDegreeTypeCSSTag = 'degree'
                    parentDegreeTypeURL = pv.degree_type.urlparam
                if pv.degree_type.code == 'DT_BACS':
                    parentDegreeTypeString = 'BS'
                    parentDegreeTypeCSSTag = 'degree'
                    parentDegreeTypeURL = pv.degree_type.urlparam
                if pv.degree_type.code == 'DT_ASSA':
                    parentDegreeTypeString = 'AA'
                    parentDegreeTypeCSSTag = 'degree'
                    parentDegreeTypeURL = pv.degree_type.urlparam
                if pv.degree_type.code == 'DT_ASSS':
                    parentDegreeTypeString = 'AS'
                    parentDegreeTypeCSSTag = 'degree'
                    parentDegreeTypeURL = pv.degree_type.urlparam


            if pv.program_type:
                parentCodeSet.add(pv.program_type.code)
                if pv.program_type.code == 'PT_MINO':
                    parentDegreeTypeCode = pv.program_type.code
                    parentDegreeTypeString = 'MINOR'
                    parentDegreeTypeCSSTag = 'program'
                    parentDegreeTypeURL = pv.program_type.urlparam
                if pv.program_type.code == 'PT_CERT':
                    parentDegreeTypeCode = pv.program_type.code
                    parentDegreeTypeString = 'CERTIFICATE'
                    parentDegreeTypeCSSTag = 'program'
                    parentDegreeTypeURL = pv.program_type.urlparam

            # set all template-bound vars to the pv object 
            pv.parentCodeSet = parentCodeSet
            pv.parentCampus = parentCampus
            pv.parentOnline = parentOnline
            pv.parentOnlinePlus = parentOnlinePlus
            pv.parentDegreeTypeCode = parentDegreeTypeCode
            pv.parentDegreeTypeString = parentDegreeTypeString
            pv.parentDegreeTypeCSSTag = parentDegreeTypeCSSTag
            pv.parentDegreeTypeURL = parentDegreeTypeURL

            
            # need to pipe-deliniate this for use in HTML
            for i,v in enumerate(pv.parentCodeSet):
                parentCodeString += v + '|'

            # remove the last charcter "|" and attach the string to the parent
            pv.parentCodeString = parentCodeString.rstrip(parentCodeString[-1])

            # finally the children need to group to their parents a single time
            # so the template doesn't need to cycle through every child for
            # each parent
            if pv.childrenCount is not 0:
                # going to nest ChildrenAssembled under Associated Parents
                pv.Children = []
                for ci,cv in enumerate(ChildrenAssembled):
                    # does the child's reference to the unique_parent_code
                    # match this parent's program code - then append to parent
                    if cv.parent_code.unique_program_code == pv.unique_program_code:
                        print(cv.title)
                        pv.Children.append(cv)

            # add this newly assembled parent object to the container object
            # that goes to the template
            ParentsAssembled.append(pv)
    else:
        # there should always be arguments
        # or the urls_converter.py should produce a 404 fail.
        pass

    return { 'Parents':ParentsAssembled, 'html':html }
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


