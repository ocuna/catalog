from django.contrib import admin
from .models import DPC_TaxLibrary,DPC_TaxonomyTerm

class Admin_DPC_libraries(admin.ModelAdmin):
    list_display = ('name','desc',)
admin.site.register(DPC_TaxLibrary,Admin_DPC_libraries)

class Admin_DPC_terms(admin.ModelAdmin):
    list_display = ('name','code','urlparam','library','desc','STATUS')
admin.site.register(DPC_TaxonomyTerm,Admin_DPC_terms)

