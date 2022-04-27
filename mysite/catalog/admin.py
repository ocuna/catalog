from django.contrib import admin
from .models import DPC_TaxLibrary,DPC_TaxonomyTerm,DPC_AcademicPage

class Admin_DPC_libraries(admin.ModelAdmin):
    list_display = ('name','desc',)
admin.site.register(DPC_TaxLibrary,Admin_DPC_libraries)

class Admin_DPC_terms(admin.ModelAdmin):
    list_display = ('name','code','urlparam','library','desc','STATUS')
admin.site.register(DPC_TaxonomyTerm,Admin_DPC_terms)

class Admin_DPC_academicpages(admin.ModelAdmin):
    list_display = ('title','unique_program_code','body_a','body_b','parent_code','program_type')
    filter_horizontal = ('taxonomy_term','department')
admin.site.register(DPC_AcademicPage,Admin_DPC_academicpages)

    

