from django.contrib import admin
from .models import DPC_TaxLibrary,DPC_TaxonomyTerm,DPC_AcademicPage

class Admin_DPC_libraries(admin.ModelAdmin):
    list_display = ('name','desc',)
admin.site.register(DPC_TaxLibrary,Admin_DPC_libraries)

class Admin_DPC_terms(admin.ModelAdmin):
    list_display = ('name','code','urlparam','library','desc','STATUS')
admin.site.register(DPC_TaxonomyTerm,Admin_DPC_terms)

class Admin_DPC_academicpages(admin.ModelAdmin):
    fields = ('title','body_a','body_b','parent_code','unique_program_code','program_type','degree_type','field_of_study','class_format','faculty_department')
    list_display = ('title','degree_type','program_type','unique_program_code','parent_code')
    filter_horizontal = ('field_of_study','class_format','faculty_department')
admin.site.register(DPC_AcademicPage,Admin_DPC_academicpages)