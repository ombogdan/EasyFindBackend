# Generated by Django 4.2.16 on 2025-04-14 09:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0003_servicetype_employee'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='employee',
            name='organization',
        ),
        migrations.AddField(
            model_name='employee',
            name='organizations',
            field=models.ManyToManyField(related_name='employees', to='myapp.organization'),
        ),
    ]
