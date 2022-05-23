from catalog.models import DPC_AcademicPage

def processAll():
    for each in DPC_AcademicPage.objects.all():
        each.save()

# useful command to wipe slugs from DB if necessary
# UPDATE catalog_dpc_academicpage SET slug = '' WHERE slug != '';