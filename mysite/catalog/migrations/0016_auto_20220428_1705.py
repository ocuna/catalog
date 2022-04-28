# Generated by Django 3.2.12 on 2022-04-28 21:05

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0015_auto_20220428_1417'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dpc_academicpage',
            name='faculty_department',
            field=models.ManyToManyField(blank=True, limit_choices_to=models.Q(('library__name', 'Faculty Department'), ('library__name', 'University Department'), _connector='OR'), related_name='academicpage_facultydepartment', to='catalog.DPC_TaxonomyTerm', verbose_name='Faculty Department'),
        ),
        migrations.AlterField(
            model_name='dpc_academicpage',
            name='title',
            field=models.CharField(max_length=255, validators=[django.core.validators.RegexValidator('^[a-zA-Z0-9,.\\(\\)\\- ]{5,150}$', message='Title must be at least 5 and max 150 Alpha-Numeric Characters, may the following punctionation characters: ,.()-_')]),
        ),
    ]
