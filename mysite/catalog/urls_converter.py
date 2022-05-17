from catalog.models import DPC_TaxonomyTerm, DPC_AcademicPage

class dmf_url_options:
    # will either match the regex or fail with 404 Response
    regex = 'discover|online|campus|onlineplus'

    # simply passes it through
    def to_python(self, value):
        return str(value)

    # simply passes it through
    def to_url(self, value):
        return str(value)

class dmf_url_taxonomy:
    # will check against the regex
    regex = '[a-z0-9\-]{3,40}'

    def to_python(self, value):
        # first, they could want "all" which isn't in the database
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

class dmf_url_academic_page:
    # will check against the regex
    regex = '[a-z\-]{3,40}'

    def to_python(self, value):
        # first, they could want "all" which isn't in the database
        if (value == 'all'):
            return str(value)
        # if it's not looking for 'all', check the DB next to see if the
        # Taxonomy Term in this url actually exists
        # if it does, it will pass the str() of the value to the view
        else:
            try:
                DPC_TaxonomyTerm.objects.filter(library="Faculty Department").get(urlparam=str(value))
                return str(value)
            except DPC_TaxonomyTerm.DoesNotExist:
                raise ValueError

    # simply passes it through
    def to_url(self, value):
        return str(value)