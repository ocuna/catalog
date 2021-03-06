# Generated by Django 3.2.12 on 2022-05-18 20:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0019_dpc_academicpage_slug'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dpc_academicpage',
            name='faculty_department',
            field=models.ManyToManyField(limit_choices_to=models.Q(('library__name', 'Faculty Department'), ('library__name', 'University Department'), _connector='OR'), related_name='academicpage_facultydepartment', to='catalog.DPC_TaxonomyTerm', verbose_name='Faculty Department'),
        ),
    ]
