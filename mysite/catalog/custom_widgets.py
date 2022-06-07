from import_export.widgets import ManyToManyWidget

# this custom widget was built because the kwarg 'field' wasn't carrying in
# the 'code' needed to properly build out the model.object.filter(), it would
# default to 'pk' which wasn't the default primary key for my objects
class CustomM2M(ManyToManyWidget):
    def __init__(self, model, separator=None, field=None, *args, **kwargs):
        if separator is None:
            separator = ','
        # IDKW, but field always comes in as None, even when set in admin.py
        if field is None:
            field = 'pk'
        self.model = model
        self.separator = separator
        self.field = field
        # added a new field that can cary the proper column name 'code' over
        self.m2mField = kwargs.get('m2mField', None)
        super(CustomM2M, self).__init__(model)

    # clean is the 'import' method that prepares the data recieved in a way
    # that will return well-formed django db - model.objects via filter()
    def clean(self, value, row=None, *args, **kwargs):
        if not value:
            return self.model.objects.none()
        if isinstance(value, (float, int)):
            ids = [int(value)]
        else:
            ids = value.split(self.separator)
            ids = filter(None, [i.strip() for i in ids])


        if self.m2mField is not None:
            id_field = '%s__in' % self.m2mField
            return self.model.objects.filter(**{id_field:ids})
        else:
            return self.model.objects.filter(**{
                '%s__in' % self.field: ids
            })

    '''
    ### ORIGINAL METHODS ###
    def clean(self, value, row=None, *args, **kwargs):
        if not value:
            return self.model.objects.none()
        if isinstance(value, (float, int)):
            ids = [int(value)]
        else:
            ids = value.split(self.separator)
            ids = filter(None, [i.strip() for i in ids])
        return self.model.objects.filter(**{
            '%s__in' % self.field: ids
        })

    def render(self, value, obj=None):
        ids = [smart_str(getattr(obj, self.field)) for obj in value.all()]
        return self.separator.join(ids)
    '''