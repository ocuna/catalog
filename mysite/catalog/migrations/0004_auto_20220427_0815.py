# Generated by Django 3.2.12 on 2022-04-27 12:15

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0003_auto_20220426_1555'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='dpc_taxlibrary',
            options={'verbose_name': 'Taxonomy Library', 'verbose_name_plural': 'Taxonomy Libraries'},
        ),
        migrations.AlterField(
            model_name='dpc_taxonomyterm',
            name='code',
            field=models.CharField(max_length=10, primary_key=True, serialize=False, validators=[django.core.validators.RegexValidator('^[A-Z0-9_]{3,10}$', message='Code must be at least 3 and max 10 Alpha-Numeric, UPPERCase with Optional Underscores Only: EX: ABC_ABC')]),
        ),
        migrations.AlterField(
            model_name='dpc_taxonomyterm',
            name='urlparam',
            field=models.CharField(max_length=20, unique=True, validators=[django.core.validators.RegexValidator('^[a-z0-9_]{3,10}$', message='Code must be at least 3 and max 10 Alpha-Numeric, LOWERCase with Optional Underscores Only: EX: ABC_ABC')]),
        ),
    ]
