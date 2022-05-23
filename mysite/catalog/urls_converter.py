from catalog.models import DPC_TaxonomyTerm, DPC_AcademicPage

###############################################################################
# Theese converters verify parameters in urls.py to ensure they are compliant #
# and will bring up actual pages or 404's will occure.                        #
# DMF stands for: Dynamic Marketing Funnel - it's the UX system that displays #
# and sorts AcademicPages for browsing                                        #
###############################################################################

# this converter needs to be one of 4 keywords, 3 of which are Taxonomy Specifc
class DMF_url_options:
    # will either match the regex or fail with 404 Response
    regex = 'discover|online|campus|onlineplus'

    # simply passes it through
    def to_python(self, value):
        return str(value)

    # simply passes it through
    def to_url(self, value):
        return str(value)

# This converter assures the parameter is a Taxonomy Term and is used to bring
# up DMF sorting functions on the DMF page
class DMF_TaxonomyTerm:
    # will check against the regex
    regex = '[a-z0-9\-]{3,40}'

    def to_python(self, value):
        # first, they could want "all" which isn't in the database, but works
        if (value == 'all'):
            return str(value)
        # if it's not looking for 'all', check the DB next to see if the
        # Taxonomy Term in this url actually exists
        # if it does, it will pass the str() of the value to the view
        else:
            try:
                DPC_TaxonomyTerm.objects.get(urlparam=str(value))
                return str(value)
            except DPC_TaxonomyTerm.DoesNotExist:
                raise ValueError

    # simply passes it through
    def to_url(self, value):
        return str(value)

# This converter assures the parameter is a Faculty Department Taxonomy Term
# and is used to bring up Academic Page Views
class AcademicPageFacultyDept:
    # will check against the regex
    regex = '[a-z\-]{10,40}'

    def to_python(self, value):
        try:
            DPC_TaxonomyTerm.objects.filter(library__name="Faculty Department").get(urlparam=str(value))
            #print('urls_converter.AcademicPageFacultyDept found:' + value)
            return str(value)
        except DPC_TaxonomyTerm.DoesNotExist:
            raise ValueError

    # simply passes it through
    def to_url(self, value):
        return str(value)

class AcademicPageSlug:
    # will check against the regex
    regex = '[a-z0-9\-]{10,100}'

    def to_python(self, value):
        try:
            # there can be duplicate slugs ... but not private keys
            DPC_AcademicPage.objects.all().filter(slug=str(value))
            #print('urls_converter.AcademicPageSlug found:' + value)
            return str(value)
        except DPC_AcademicPage.DoesNotExist:
            raise ValueError

    # simply passes it through
    def to_url(self, value):
        return str(value)

class AcademicPagePrimaryKey:
    # will check against the regex
    regex = '[0-9]{1,4}'

    def to_python(self, value):
        try:
            DPC_AcademicPage.objects.get(pk=int(value))
            #print('urls_converter.AcademicPagePrimaryKey' + value)
            return str(value)
        except DPC_AcademicPage.DoesNotExist:
            raise ValueError

    # simply passes it through
    def to_url(self, value):
        return str(value)