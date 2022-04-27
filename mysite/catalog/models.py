from django.contrib import admin
from django.core.validators import RegexValidator
from django.db import models
# https://django-model-utils.readthedocs.io/en/latest
from model_utils.models import StatusModel
from model_utils import Choices


''' PROROBLY TRASH 
###############################################################################
# The following are componants that share a relationship with taxonomy terms  #
# they must be unique to function correclty.                                  #
###############################################################################

# short set of characters like a UUID that identify taxonomy terms
class DPC_taxonomy_code(models.Model):
    dpc_code = models.CharField(max_length=10, unique = True)

class DPC_taxonomy_code(models.Model):
    dpc_code = models.CharField(max_length=10, unique = True)

class DPC_url_param(models.Model):
    dpc_url_param = models.CharField(max_length=10, unique = True)

###############################################################################
# The following are "taxonomy terms" associated with degree programs          #
# Degree programs are configurd with this to  sort / organize / display       #
###############################################################################
'''
# Libraries are many-to-one relationships with TaxTerms
# a UNIQUE TaxonomyTerm can ONLY reside in a SINGLE TaxonmyLibrary
class DPC_TaxLibrary(models.Model):
    name = models.CharField(max_length=100,unique=True,null=False)
    desc = models.CharField(max_length=255)
    def __str__(self):
        return self.name
    class Meta:
        verbose_name = 'Taxonomy Library'
        verbose_name_plural = 'Taxonomy Libraries'

class DPC_TaxonomyTerm(StatusModel):
    code = models.CharField(
        max_length=10,
        primary_key=True,
        validators=[
            RegexValidator('^[A-Z0-9_]{3,10}$',
            message='Code must be at least 3 and max 10 Alpha-Numeric, UPPERCase with Optional Underscores Only: EX: ABC_ABC')
        ])
    name = models.CharField(max_length=100,unique=True)
    urlparam = models.CharField(
        max_length=30,
        unique=True,
        validators=[
        RegexValidator('^[a-z0-9\-]{3,30}$',
            message='Code must be at least 3 and max 30 Alpha-Numeric, LOWERCase with Optional Hyphens Only: EX: ABC-ABC')
        ])
    desc = models.CharField(max_length=255,blank=True,default='')
    STATUS = Choices('published','removed')
    library = models.ForeignKey(DPC_TaxLibrary, on_delete=models.CASCADE)
    def __str__(self):
        return self.name
    class Meta:
        verbose_name = 'Taxonomy Term'




    
