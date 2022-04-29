from django.contrib import admin
from django.core.validators import RegexValidator
from django.db import models
from django.db.models import Q
from django.utils.html import format_html

# https://django-model-utils.readthedocs.io/en/latest
from model_utils.models import StatusModel
from model_utils import Choices

###############################################################################
# The following are componants that share a relationship with taxonomy terms  #
# they must be unique to function correclty.                                  #
###############################################################################
# Libraries are many-to-one relationships with TaxTerms
# a UNIQUE TaxonomyTerm can ONLY reside in a SINGLE TaxonomyLibrary
class DPC_TaxLibrary(models.Model):
    name = models.CharField(max_length=100,unique=True,null=False)
    desc = models.CharField(max_length=255)
    def __str__(self):
        return self.name
    class Meta:
        verbose_name = 'Taxonomy Library'
        verbose_name_plural = 'Taxonomy Libraries'

###############################################################################
# The following are "taxonomy terms" associated with degree programs          #
# Degree programs are configurd with this to  sort / organize / display       #
###############################################################################
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
        max_length=40,
        unique=True,
        validators=[
        RegexValidator('^[a-z0-9\-]{3,40}$',
            message='Code must be at least 3 and max 30 Alpha-Numeric, LOWERCase with Optional Hyphens Only: EX: ABC-ABC')
        ])
    desc = models.CharField(max_length=255,blank=True,default='')
    STATUS = Choices('published','removed')
    library = models.ForeignKey(DPC_TaxLibrary, on_delete=models.CASCADE)
    def __str__(self):
        return self.name
    class Meta:
        verbose_name = 'Taxonomy Term'


###############################################################################
# Following are the "academic pages" that display degrees, certificates etc.  #
###############################################################################
class DPC_AcademicPage(StatusModel):
    title = models.CharField(
        max_length=255,
        validators=[
            RegexValidator('^[a-zA-Z0-9,.\(\)\- ]{5,150}$',
            message='Title must be at least 5 and max 150 Alpha-Numeric Characters, may the following punctionation characters: ,.()-_'),
        ]
    )
    degree_type = models.ForeignKey(
        DPC_TaxonomyTerm,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        limit_choices_to=Q(library__name='Degree Type'),
        related_name='academicpage_degreetype',
        verbose_name='Degree Type'
    )

    field_of_study = models.ManyToManyField(
        DPC_TaxonomyTerm,
        blank=True,
        limit_choices_to=Q(library__name='Field of Study'),
        related_name='academicpage_fieldofstudy',
        verbose_name='Field of Study',
    )

    program_type = models.ForeignKey(
        DPC_TaxonomyTerm,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        limit_choices_to=Q(library__name='Program Type'),
        related_name='academicpage_programtype',
        verbose_name='Program Type'
    )

    class_format = models.ManyToManyField(
        DPC_TaxonomyTerm,
        blank=True,
        limit_choices_to=Q(library__name='Class Format'),
        related_name='academicpage_classformat',
        verbose_name='Class Format'
    )

    faculty_department = models.ManyToManyField(
        DPC_TaxonomyTerm,
        blank=True,
        limit_choices_to=(Q(library__name='Faculty Department') | Q(library__name='University Department')),
        related_name='academicpage_facultydepartment',
        verbose_name='Faculty Department'
    )

    body_a = models.TextField(
        help_text="HTML in the top portion of the page.  Not HTML validated, Do not edit here, be careful.",
        verbose_name='Body A HTML',
        blank=True,
        default='')

    body_b = models.TextField(
        help_text="HTML in the bottom portion of the page.  Not HTML validated, Do not edit here, be careful.",
        verbose_name='Body B HTML',
        blank=True,
        default='')

    unique_program_code = models.CharField(
        max_length=30,
        unique=True,
        help_text="Must be unique.  Is used to identify parent/child relationships of programs.  Such as a concentration of a major.",
        validators=[
            RegexValidator('^[a-zA-Z0-9_\-]{6,30}$',
            message='Code must be unique.  Code must be at least 6 and max 30 Alpha-Numeric Characters, may include underscores and dashes')
        ])
        
    parent_code = models.ForeignKey(
        'self',
        to_field='unique_program_code',
        help_text="This will unite this program with another program in a relationship such as Major/Concentration.",
        on_delete=models.SET_DEFAULT, 
        blank=True,
        null=True,
        default='',
        limit_choices_to=Q(program_type_id='PT_DEGR'),
        verbose_name='Parent Code'
    )

    STATUS = Choices('published','removed')
    def __str__(self):
        return ("{} . . . {}").format(self.title, self.degree_type)
    class Meta:
        verbose_name = 'Academic Degree Page'
        verbose_name_plural = 'Academic Degree Pages'

    
