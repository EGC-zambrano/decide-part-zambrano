# Generated by Django 4.1 on 2022-11-17 18:38

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("voting", "0003_auto_20180605_0842"),
    ]

    operations = [
        migrations.AlterField(
            model_name="voting",
            name="postproc",
            field=models.JSONField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="voting",
            name="tally",
            field=models.JSONField(blank=True, null=True),
        ),
    ]
