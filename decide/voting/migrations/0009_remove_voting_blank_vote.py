# Generated by Django 4.1 on 2023-11-20 18:25

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('voting', '0008_voting_blank_vote'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='voting',
            name='blank_vote',
        ),
    ]
