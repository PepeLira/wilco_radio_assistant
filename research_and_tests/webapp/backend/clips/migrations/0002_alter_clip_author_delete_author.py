# Generated by Django 5.1 on 2024-08-21 00:08

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
        ('clips', '0001_initial'),
        ('reports', '0002_alter_report_author'),
    ]

    operations = [
        migrations.AlterField(
            model_name='clip',
            name='author',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounts.author'),
        ),
        migrations.DeleteModel(
            name='Author',
        ),
    ]
