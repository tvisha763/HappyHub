# Generated by Django 4.0.6 on 2022-09-24 22:02

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('APP', '0003_chatgroup_groupmembership_chatgroup_members'),
    ]

    operations = [
        migrations.AlterField(
            model_name='groupmembership',
            name='date_joined',
            field=models.DateField(default=django.utils.timezone.now),
        ),
    ]
