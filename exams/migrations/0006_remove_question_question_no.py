# Generated by Django 3.0.5 on 2020-07-03 23:25

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('exams', '0005_remove_option_option_name'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='question',
            name='question_no',
        ),
    ]
