# Generated by Django 3.2.16 on 2023-07-19 15:16

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='subscription',
            name='no_self_subscription',
        ),
    ]
