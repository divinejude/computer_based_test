# Generated by Django 3.0.5 on 2020-07-03 23:16

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('exams', '0004_auto_20200621_0217'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='option',
            name='option_name',
        ),
    ]
