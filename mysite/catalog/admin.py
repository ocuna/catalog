from django.contrib import admin
from .models import DPC_TaxLibrary,DPC_TaxonomyTerm,DPC_AcademicPage
from import_export import fields,resources
from import_export.widgets import ForeignKeyWidget,ManyToManyWidget
from .custom_widgets import CustomM2M

from import_export.admin import ImportExportModelAdmin

class termsResource(resources.ModelResource):
    library = fields.Field(
        column_name='library_id',
        attribute='library',
        widget=ForeignKeyWidget(model=DPC_TaxLibrary, field='id')
    )
    class Meta:
        model = DPC_TaxonomyTerm
        import_id_fields = ('code',)
        fields = ('code', 'status', 'status_changed', 'name', 'urlparam', 'desc', 'weight')

class academicPageResource(resources.ModelResource):
    parent_code = fields.Field(
        column_name='parent_code_id',
        attribute='parent_code',
        widget=ForeignKeyWidget(model=DPC_AcademicPage, field='unique_program_code')
    )

    faculty_department = fields.Field(
        column_name='faculty_department',
        attribute='faculty_department',
        # Custom M2M was reqauired here, because for some reason field='code'
        # wasn't being passed through to the normal import 'clean()' method
        # within the ManyToManyWidget() class - it did work on export or
        # 'render()' but didn't work at all on 'clean()' - it would revert to
        # "pk" which is normally correct, but my model specifies the primary
        # key as 'code'
        widget=CustomM2M(model=DPC_TaxonomyTerm, field='code', m2mField='code')
    )

    program_type = fields.Field(
        column_name='program_type_id',
        attribute='program_type',
        widget=ForeignKeyWidget(model=DPC_TaxonomyTerm, field='code')
    )

    degree_type = fields.Field(
        column_name='degree_type_id',
        attribute='degree_type',
        widget=ForeignKeyWidget(model=DPC_TaxonomyTerm, field='code')
    )

    field_of_study = fields.Field(
        column_name='field_of_study',
        attribute='field_of_study',
        widget=CustomM2M(model=DPC_TaxonomyTerm, field='code', m2mField='code')
    )
    class_format = fields.Field(
        column_name='class_format',
        attribute='class_format',
        widget=CustomM2M(model=DPC_TaxonomyTerm, field='code', m2mField='code')
    )
    faculty_department = fields.Field(
        column_name='faculty_department',
        attribute='faculty_department',
        widget=CustomM2M(model=DPC_TaxonomyTerm, field='code', m2mField='code')
    )

    class Meta:
        fields = ('id','title', 'status', 'status_changed', 'slug', 'unique_program_code','faculty_department__code')
        exclude = ('body_a','body_b','slug')
        model = DPC_AcademicPage

class Admin_DPC_libraries(ImportExportModelAdmin):
    list_display = ('name','desc',)
admin.site.register(DPC_TaxLibrary,Admin_DPC_libraries)

class Admin_DPC_terms(ImportExportModelAdmin):
    resource_class = termsResource
    list_display = ('weight','name','code','urlparam','library','desc','STATUS',)
admin.site.register(DPC_TaxonomyTerm,Admin_DPC_terms)

class Admin_DPC_academicpages(ImportExportModelAdmin):
    resource_class = academicPageResource
    fields = ('title','slug','degree_type','status','field_of_study','program_type','class_format','faculty_department','body_a','body_b','unique_program_code','parent_code')
    list_display = ('title','degree_type','program_type','unique_program_code','parent_code')
    filter_horizontal = ('field_of_study','class_format','faculty_department')
    readonly_fields = ('slug',)
    # I don't like this is global.  I originally wanted to sort only the
    # parent_code form admin, but I couldn't figure it out in time
    # not important enough to take all day.
    ordering = ['title']
    
admin.site.register(DPC_AcademicPage,Admin_DPC_academicpages)