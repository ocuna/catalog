import ast
from django.db.models import Q,F,Value,Subquery,Prefetch
from django.db.models.functions import Concat
from catalog.models import DPC_TaxLibrary, DPC_TaxonomyTerm, DPC_AcademicPage
from catalog.utils import _clean_title

# calls the DB for all child programs that match this parentCode
def _academicPage_parentcode_to_html_dpc_child_display(parentCode):
    children = DPC_AcademicPage.objects.filter(parent_code=parentCode)
    count = int(children.count())
    return {'children':children,'count':count}

# calls the DB for all taxonomy terms matching the tax term
# from: _convert_object_array_to_html_option_list()
def _taxonomyTerm_objects_to_html_option_list(tax_term='',url_args=None):
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
# args contains URL parameters that mostly describe taxonomy terms to filter
# in some cases like all,discover these are non-taxonomy urls the sepecify an 
# inclusive filter style.  Also, transforming the output can also be modified
# by including 'union' into the function which will create a different sort
# Additinal paraemters passed into args control html formating such as
# 'programkey' and 'resetbutton' 
def _academicPage_objects_to_html_dmf_list(*args):
    # the arguments passed won't necessarilly be used in the function, some are
    # interspersed with triggers
    cleanargs = []
    # function uses trigger words: deliminted and union
    delimited = False
    union = False
    exclude = False
    resetbutton = False
    programkey = False
    exclusions = []

    # these lists are formed after for loops process the contents and then 
    # attach specific data that is formatted for the templates downstreamm
    ParentsAssembled = []
    ChildrenAssembled = []

    # there will always be args because urls_converter.py shoud catch it ...
    # but just in case...
    if args:
        # if this trigger 'delimited_string' is detected in the args, it will
        # remake the args by transforming the 2nd argument (which should be a
        # space delimited string) into an tuple replacing args
        if args[0][0] == 'delimited_string':
            delimited = True
            # maybe the second arg has no delimiter:
            if " " in args[0][1]:
                string = "('" + args[0][1].replace(" ","','") + "')"
                args = [ast.literal_eval(string)]
            else:
                # need to reassemble the nested args structure
                args = tuple([[args[0][1]]])

        # detect exclusions
        for i,arg in enumerate(args[0]):
            if 'exclude:' in arg:
                exclude = True
                exclusions.append(arg.replace('exclude:',''))

        # check if union apears.
        for i,arg in enumerate(args[0]):
            if arg == 'union':
                union = True
 
        # check if resetbutton apears.
        for i,arg in enumerate(args[0]):
            if arg == 'resetbutton':
                args[0].remove(arg)
                resetbutton = True

        # check if programkey apears.
        for i,arg in enumerate(args[0]):
            if arg == 'programkey':
                args[0].remove(arg)
                programkey = True

        # delimited changes the structure
        # in any case we need to remove union
        if not delimited:
            for i,arg in enumerate(args[0]):
                cleanargs.append(arg)
        elif delimited:
            for i,arg in enumerate(args[0]):
                cleanargs.append(arg)

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


        # if union, simply look for all parents that match either
        # argument and add them together
        if union:
            Add_All_Parents = DPC_AcademicPage.objects.none()
            # the *args are passed through two layers of catalog_tags by this
            # point which means it is nested within args
            for i,arg in enumerate(cleanargs):
                if i < 1:
                    Add_All_Parents = Parents_PreFetch_Kids.filter(
                        Q(degree_type__urlparam=arg) |
                        Q(field_of_study__urlparam=arg) |
                        Q(program_type__urlparam=arg) |
                        Q(faculty_department__urlparam=arg) |
                        Q(class_format__urlparam=arg))
                else:
                    Add_All_Parents = Add_All_Parents | Parents_PreFetch_Kids.filter(
                        Q(degree_type__urlparam=arg) |
                        Q(field_of_study__urlparam=arg) |
                        Q(program_type__urlparam=arg) |
                        Q(faculty_department__urlparam=arg) |
                        Q(class_format__urlparam=arg))
            Parents_PreFetch_Kids = Add_All_Parents.distinct()
        
        # if there is a sidebar, continue filter by each argument
        else:
            for i,arg in enumerate(cleanargs):
                if ('exclude:' not in arg and
                    'union' not in arg):
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

        # cycles through the exclusion list to find arguments that should be
        # excluded from this query
        if exclude:
            for i,arg in enumerate(exclusions):
                Parents_PreFetch_Kids = Parents_PreFetch_Kids.exclude(
                    Q(degree_type__urlparam=arg) |
                    Q(program_type__urlparam=arg) |
                    Q(faculty_department__urlparam=arg))


        Parents = (Parents_PreFetch_Kids
            .order_by(F('degree_type__weight').asc(nulls_last=True),
                F('program_type__weight').asc(nulls_last=True),
                F('class_format__weight').asc(nulls_last=True),
                'title')
            .distinct())

        # 8 quries at this point
        # Prior to this I was retaining the Parents and Children as DB Objects
        # this would re-run the queries during enumerate() loops originally
        #Parents = list(Parents.values(id,status,title,slug,degree_type_id,program_type_id,body_a,body_b,unique_program_code,parent_code_id))
        #Children = list(Children.values(id,status,title,slug,degree_type_id,program_type_id,body_a,body_b,unique_program_code,parent_code_id))

        

        Parents = list(Parents.values('id','status','title','slug','degree_type_id','program_type_id','unique_program_code','parent_code_id','dpc_academicpage'))
        Children = list(Children.values('id','status','title','slug','degree_type_id','program_type_id','unique_program_code','parent_code_id'))
        FK_degree_type = list(DPC_AcademicPage.objects.values('id','degree_type','degree_type__urlparam'))
        FK_program_type = list(DPC_AcademicPage.objects.values('id','program_type','program_type__urlparam'))
        M2M_field_of_study = list(DPC_AcademicPage.objects.values('id','field_of_study','field_of_study__urlparam'))
        M2M_faculty_department = list(DPC_AcademicPage.objects.values('id','faculty_department','faculty_department__urlparam'))
        M2M_class_format = list(DPC_AcademicPage.objects.values('id','class_format','class_format__name','class_format__urlparam'))

        for cv in Children:
            childCodeString = ''
            childClassFormatString = ''
            childClassFormatList = []
            childCodeList = []
            childCodeSet = set()
            for v in M2M_field_of_study:
                if v['id'] == cv['id']:
                    if v['field_of_study']:
                        childCodeSet.add(v['field_of_study'])

            for v in M2M_faculty_department:
                if v['id'] == cv['id']:
                    if v['faculty_department']:
                        childCodeSet.add(v['faculty_department'])

            for v in M2M_class_format:
                if v['id'] == cv['id']:
                    childCodeSet.add(v['class_format'])
                    if v['class_format__name']:
                        childClassFormatString += str(v['class_format__name']) + " " 
 
            if cv['degree_type_id']:
                childCodeSet.add(cv['degree_type_id'])

            if cv['program_type_id']:
                childCodeSet.add(cv['program_type_id'])

            cv['childCodeSet'] = childCodeSet
            # need to pipe-deliniate this for use in HTML
            for i,v in enumerate(childCodeSet):
                if v:
                    childCodeString += str(v) + '|'

            # remove the last charcter "|" and attach the string to the parent
            cv['childCodeString'] = childCodeString.rstrip(childCodeString[-1])
            ChildrenAssembled.append(cv)

        for pv in Parents:
            parentCodeString = ''
            parentCodeList = []
            parentCodeSet = set()
            parentDegreeTypeCode = ''
            parentDegreeTypeString = ''
            parentDegreeTypeURL = ''
            parentClassFormatString = ''
            parentOnline = False
            parentOnlinePlus = False
            parentCampus = False
            parentOnline = False
            parentOnlinePlus = False

            #loop through all the children of this parent, get all codes that
            # exist in children and add them to the parents.
            for c in ChildrenAssembled:
                if c['parent_code_id']:
                    if pv['unique_program_code'] == c['parent_code_id']:
                        for code in c['childCodeSet']:
                            parentCodeSet.add(code)

            # add the codes from the parent
            parentCodeSet.add(pv['degree_type_id'])
            parentCodeSet.add(pv['program_type_id'])


            for v in M2M_class_format:
                if v['id'] == pv['id']:
                    childCodeSet.add(v['class_format'])
                    if pv['id'] == 'F_CAMP':
                        parentCampus = True
                    if pv['id'] == 'F_ONLI':
                        parentOnline = True
                    if pv['id'] == 'F_VIRT':
                        parentOnlinePlus = True
                    if v['class_format__name']:
                        parentClassFormatString += str(v['class_format__name']) + " "

            for v in M2M_field_of_study:
                if v['id'] == pv['id']:
                    if v['field_of_study']:
                        parentCodeSet.add(v['field_of_study'])

            for v in M2M_faculty_department:
                if v['id'] == pv['id']:
                    if v['faculty_department']:
                        parentCodeSet.add(v['faculty_department'])


            # this is simply a case-based system designed to create classes and
            # on the template it's passed to for proper styling based on the
            # degree or program type below 
            if pv['degree_type_id']:
                parentDegreeTypeCode = pv['degree_type_id']
                if pv['degree_type_id'] == 'DT_MAST':
                    parentDegreeTypeString = 'M'
                    parentDegreeTypeCSSTag = 'degree'
                    parentDegreeTypeURL = 'masters'
                if pv['degree_type_id'] == 'DT_BACA':  
                    parentDegreeTypeString = 'BA'
                    parentDegreeTypeCSSTag = 'degree'
                    parentDegreeTypeURL = 'bachelor-of-arts'
                if pv['degree_type_id'] == 'DT_BACS':
                    parentDegreeTypeString = 'BS'
                    parentDegreeTypeCSSTag = 'degree'
                    parentDegreeTypeURL = 'bachelor-of-science'
                if pv['degree_type_id'] == 'DT_ASSA':
                    parentDegreeTypeString = 'AA'
                    parentDegreeTypeCSSTag = 'degree'
                    parentDegreeTypeURL = 'associate-of-arts'
                if pv['degree_type_id'] == 'DT_ASSS':
                    parentDegreeTypeString = 'AS'
                    parentDegreeTypeCSSTag = 'degree'
                    parentDegreeTypeURL = 'associate-of-science'


            if pv['program_type_id']:
                if pv['program_type_id'] == 'PT_MINO':
                    parentDegreeTypeCode = pv['program_type_id']
                    parentDegreeTypeString = 'MINOR'
                    parentDegreeTypeCSSTag = 'program'
                    parentDegreeTypeURL = 'minor'
                if pv['program_type_id'] == 'PT_CERT':
                    parentDegreeTypeCode = pv['program_type_id']
                    parentDegreeTypeString = 'CERTIFICATE'
                    parentDegreeTypeCSSTag = 'program'
                    parentDegreeTypeURL = 'certificate'

            # set all template-bound vars to the pv object 
            pv['parentCodeSet'] = parentCodeSet
            pv['parentCampus'] = parentCampus
            pv['parentOnline'] = parentOnline
            pv['parentOnlinePlus'] = parentOnlinePlus
            pv['parentDegreeTypeCode'] = parentDegreeTypeCode
            pv['parentDegreeTypeString'] = parentDegreeTypeString
            pv['parentDegreeTypeCSSTag'] = parentDegreeTypeCSSTag
            pv['parentDegreeTypeURL'] = parentDegreeTypeURL
            pv['parentClassFormatString'] = parentClassFormatString.strip()
            pv['cleanTitle'] = _clean_title(pv['title'])

            for v in pv['parentCodeSet']:
                if v:
                    parentCodeString += str(v) + '|'

            # remove the last charcter "|" and attach the string to the parent
            pv['parentCodeString'] = parentCodeString.rstrip(parentCodeString[-1])


            # finally the children need to group to their parents a single time
            # so the template doesn't need to cycle through every child for
            # each parent
            for ci,cv in enumerate(ChildrenAssembled):
                # does the child's reference to the unique_parent_code
                # match this parent's program code - then append to parent
                if cv['parent_code_id'] == pv['unique_program_code']:
                    pv['Children'] = []
                    pv['Children'].append(cv)

            # add this newly assembled parent object to the container object
            # that goes to the template
            ParentsAssembled.append(pv)

        '''
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
            parentClassFormatString = ''
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
            for i,v in enumerate(pv.class_format.values_list('name')):
                for ii,vv in enumerate(v):
                    if vv :
                        parentClassFormatString += vv + " "

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
            pv.parentClassFormatString = parentClassFormatString.strip()
            pv.cleanTitle = _clean_title(pv.title)

            
            # need to pipe-deliniate this for use in HTML
            for i,v in enumerate(pv.parentCodeSet):
                parentCodeString += v + '|'

            # remove the last charcter "|" and attach the string to the parent
            pv.parentCodeString = parentCodeString.rstrip(parentCodeString[-1])

            # finally the children need to group to their parents a single time
            # so the template doesn't need to cycle through every child for
            # each parent
            if pv.childrenCount != 0:
                # going to nest ChildrenAssembled under Associated Parents
                pv.Children = []
                for ci,cv in enumerate(ChildrenAssembled):
                    # does the child's reference to the unique_parent_code
                    # match this parent's program code - then append to parent
                    if cv.parent_code.unique_program_code == pv.unique_program_code:
                        pv.Children.append(cv)

            # add this newly assembled parent object to the container object
            # that goes to the template
            ParentsAssembled.append(pv)
    else:
        # there should always be arguments
        # or the urls_converter.py should produce a 404 fail.
        pass
    '''
    #ParentsAssembled = []
    #ChildrenAssembled = []
    return { 'Parents':ParentsAssembled, 'resetbutton':resetbutton, 'programkey':programkey}
    # GOT IT!

    # P.objects.all().filter(parent_code__isnull=True).select_related('parent_code').prefetch_related('parent_code__parent_code')[1].dpc_academicpage_set.values('title')



'''
# this loops through the Children and assembles their taxonomy codes
# This is simliar but more simple then how the parents work 
for ci,cv in enumerate(Children):
    childCodeString = ''
    childClassFormatString = ''
    childClassFormatList = []
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

    for i,v in enumerate(cv.class_format.values_list('name')):
        for ii,vv in enumerate(v):
            if vv :
                childClassFormatString += vv + " " 

    if cv.program_type:
        childCodeSet.add(cv.program_type.code)

    if cv.degree_type:
        childCodeSet.add(cv.degree_type.code)

    cv.cleanTitle = _clean_title(cv.title)
    cv.childClassFormatString = childClassFormatString.strip()
    cv.childCodeSet = childCodeSet

    # need to pipe-deliniate this for use in HTML
    for i,v in enumerate(cv.childCodeSet):
        childCodeString += v + '|'

    # remove the last charcter "|" and attach the string to the parent
    cv.childCodeString = childCodeString.rstrip(childCodeString[-1])
    ChildrenAssembled.append(cv)
'''