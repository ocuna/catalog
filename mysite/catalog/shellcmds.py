from catalog.models import DPC_AcademicPage

def processAll():
    for each in DPC_AcademicPage.objects.all():
        each.save()